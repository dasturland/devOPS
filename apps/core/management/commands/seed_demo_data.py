"""Idempotent demo-data seeder (FR-28).

Running this command multiple times does not create duplicates: every object is
created with ``get_or_create`` / ``update_or_create`` keyed by a natural, stable
identifier. On completion the demo account credentials are printed so the README
and reviewers can log in immediately.

Creates: 1 admin, 2 managers, 5 customers, 3 cafes, 30+ tables, 40+ reservations
across every lifecycle status, and several reviews.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.cafes.models import Cafe, Zone, ZoneType
from apps.reservations.models import Reservation, ReservationStatus
from apps.reviews.models import Review
from apps.tables.models import Table

User = get_user_model()

DEMO_PASSWORD = "demo12345"

# Rotating set of statuses so the seed covers the full lifecycle (FR-16).
STATUS_CYCLE = [
    ReservationStatus.PENDING,
    ReservationStatus.CONFIRMED,
    ReservationStatus.COMPLETED,
    ReservationStatus.CANCELLED,
    ReservationStatus.REJECTED,
    ReservationStatus.NO_SHOW,
]


class Command(BaseCommand):
    """Populate the database with a realistic, idempotent demo dataset."""

    help = "Namunaviy demo ma'lumotlarni (idempotent) yaratadi (FR-28)."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--reservations",
            type=int,
            default=48,
            help="Yaratiladigan bronlar soni (standart: 48).",
        )

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        count = int(options["reservations"])

        admin = self._user("admin@tablereserve.uz", "ADMIN", "Admin", is_super=True)
        managers = [
            self._user("manager1@tablereserve.uz", "MANAGER", "Jamshid"),
            self._user("manager2@tablereserve.uz", "MANAGER", "Dilnoza"),
        ]
        customers = [
            self._user(f"customer{i}@tablereserve.uz", "CUSTOMER", f"Mijoz{i}") for i in range(1, 6)
        ]

        cafes = self._cafes(managers)
        tables = self._tables(cafes)
        reservations = self._reservations(customers, tables, count)
        self._reviews(reservations)

        self.stdout.write(self.style.SUCCESS("Demo ma'lumotlar tayyor."))
        self.stdout.write("")
        self.stdout.write(f"Demo akkauntlar (parol: {DEMO_PASSWORD}):")
        self.stdout.write("  Admin     : admin@tablereserve.uz")
        self.stdout.write("  Menejer 1 : manager1@tablereserve.uz")
        self.stdout.write("  Menejer 2 : manager2@tablereserve.uz")
        self.stdout.write("  Mijozlar  : customer1..5@tablereserve.uz")
        self.stdout.write("")
        self.stdout.write(
            f"Yaratilgan: {Cafe.objects.count()} kafe, "
            f"{Table.objects.count()} stol, "
            f"{Reservation.objects.count()} bron, "
            f"{Review.objects.count()} sharh."
        )
        # Keep the admin reference silent-used so linters stay happy.
        assert admin.pk is not None

    # ------------------------------------------------------------------
    # Helpers (idempotent via get_or_create / update_or_create)
    # ------------------------------------------------------------------
    def _user(self, email: str, role: str, first_name: str, is_super: bool = False):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "role": role,
                "first_name": first_name,
                "is_staff": is_super,
                "is_superuser": is_super,
            },
        )
        # Always (re)set the demo password so credentials stay predictable.
        user.set_password(DEMO_PASSWORD)
        user.role = role
        user.is_staff = is_super
        user.is_superuser = is_super
        user.save()
        return user

    def _cafes(self, managers: list) -> list[Cafe]:
        data = [
            ("Qahva Uyi", "qahva-uyi", "Toshkent, Amir Temur 1", managers[0]),
            ("Terrasa Lounge", "terrasa-lounge", "Toshkent, Buyuk Ipak 22", managers[0]),
            ("Nur Cafe", "nur-cafe", "Samarqand, Registon 5", managers[1]),
        ]
        cafes = []
        for name, slug, address, manager in data:
            cafe, _ = Cafe.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "address": address,
                    "phone": "+998901112233",
                    "manager": manager,
                    "opening_time": time(9, 0),
                    "closing_time": time(23, 0),
                    "description": f"{name} - qulay va iliq muhit.",
                    "is_active": True,
                },
            )
            cafes.append(cafe)
        return cafes

    def _tables(self, cafes: list[Cafe]) -> list[Table]:
        tables: list[Table] = []
        zone_specs = [
            ("Asosiy zal", ZoneType.HALL),
            ("Terrasa", ZoneType.TERRACE),
            ("VIP", ZoneType.VIP),
        ]
        for cafe in cafes:
            for zname, ztype in zone_specs:
                zone, _ = Zone.objects.get_or_create(
                    cafe=cafe,
                    name=zname,
                    defaults={"zone_type": ztype},
                )
                # 4 tables per zone => 3 cafes * 3 zones * 4 = 36 tables (>= 30).
                for n in range(1, 5):
                    number = f"{zname[0]}{n}"
                    table, _ = Table.objects.update_or_create(
                        zone=zone,
                        number=number,
                        defaults={"capacity": 2 + n, "status": "AVAILABLE"},
                    )
                    tables.append(table)
        return tables

    def _reservations(self, customers: list, tables: list[Table], count: int) -> list[Reservation]:
        reservations: list[Reservation] = []
        base = timezone.localtime(timezone.now()).replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0,
        )
        for i in range(count):
            table = tables[i % len(tables)]
            customer = customers[i % len(customers)]
            status = STATUS_CYCLE[i % len(STATUS_CYCLE)]
            # Spread reservations across past and future days and times so the
            # dashboard and "my reservations" filters show realistic data.
            day_offset = (i % 20) - 10  # -10 .. +9 days
            hour = 10 + (i % 10)  # within 09:00-23:00 working window
            start_naive = (base + timedelta(days=day_offset)).replace(hour=hour)
            start_time = self._aware(start_naive)

            reservation, _ = Reservation.objects.update_or_create(
                customer=customer,
                table=table,
                start_time=start_time,
                defaults={
                    "duration_minutes": 120,
                    "guests_count": 2 + (i % 3),
                    "status": status,
                    "note": "Demo bron",
                },
            )
            reservations.append(reservation)
        return reservations

    def _reviews(self, reservations: list[Reservation]) -> None:
        completed = [r for r in reservations if r.status == ReservationStatus.COMPLETED]
        comments = [
            "Ajoyib xizmat va iliq muhit!",
            "Stol toza va qulay edi.",
            "Yana albatta tashrif buyuraman.",
            "Narxlar o'rtacha, sifat yaxshi.",
        ]
        for i, reservation in enumerate(completed):
            Review.objects.update_or_create(
                reservation=reservation,
                defaults={
                    "cafe": reservation.table.zone.cafe,
                    "author": reservation.customer,
                    "rating": 3 + (i % 3),
                    "comment": comments[i % len(comments)],
                },
            )

    @staticmethod
    def _aware(value: datetime) -> datetime:
        if timezone.is_naive(value):
            return timezone.make_aware(value)
        return value
