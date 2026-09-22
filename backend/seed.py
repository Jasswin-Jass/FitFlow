import asyncio
import os
import sys
import uuid
import random
from datetime import date, datetime, timedelta, timezone

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.session import AsyncSessionLocal, engine
from app.database.base import Base
from app.core.security import get_password_hash
from app.models.gym import Gym
from app.models.user import User
from app.models.member import Member
from app.models.trainer import Trainer
from app.models.trainer_assignment import TrainerMemberAssignment
from app.models.trainer_review import TrainerReview
from app.models.membership_plan import MembershipPlan
from app.models.membership import Membership
from app.models.payment import Payment
from app.models.summary_metrics import SummaryMetric
from app.analytics.metrics import (
    calculate_active_members,
    calculate_mrr,
    calculate_renewal_rate,
    get_at_risk_members_data,
)

# Realistic Tamil Nadu Names
FIRST_NAMES_MALE = [
    "Karthik", "Arun", "Vignesh", "Deepak", "Suresh", "Rajesh", "Harish", "Gautham",
    "Balaji", "Sanjay", "Vijay", "Naveen", "Manoj", "Praveen", "Ashwin", "Siddharth",
    "Dinesh", "Kishore", "Surya", "Saravanan", "Murugan", "Anand", "Ramesh", "Raghav",
    "Madhavan", "Venkatesh", "Prashanth", "Ranjith", "Shankar", "Ajith"
]
FIRST_NAMES_FEMALE = [
    "Ananya", "Deepa", "Divya", "Meenakshi", "Kavitha", "Pavithra", "Nithya", "Swetha",
    "Pooja", "Sandhya", "Radhika", "Lavanya", "Harini", "Keerthi", "Sangeetha", "Aarthi",
    "Lakshmi", "Preethi", "Sneha", "Sindhu", "Gayathri", "Shalini", "Yamini", "Varsha"
]
LAST_NAMES = [
    "Ramesh", "Sundaram", "Natarajan", "Subramanian", "Kumar", "Balaji", "Raghavan",
    "Venkat", "Raman", "Mani", "Sridhar", "Shankar", "Mohan", "Prakash", "Swaminathan",
    "Iyer", "Chettiar", "Gounder", "Pillai", "Naidu", "Krishnan", "Kannan"
]

OCCUPATIONS = [
    "Software Engineer", "Product Manager", "Data Analyst", "Architect", "Doctor",
    "Chartered Accountant", "College Professor", "Entrepreneur", "Marketing Manager",
    "Bank Manager", "Civil Engineer", "UX Designer", "Fitness Enthusiast", "Lawyer"
]

CITIES_TN = ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"]

FITNESS_GOALS = ["Weight Loss", "Muscle Gain", "Endurance", "Flexibility", "General Fitness"]
ACQ_SOURCES = ["Walk-in", "Referral", "Social Media", "Google Search", "Flyer/Local Ad"]
TRAINING_TIMES = ["Morning", "Afternoon", "Evening", "Night"]


async def seed_data():
    print("Beginning comprehensive FitFlow Business Intelligence database seeding...")

    async with engine.begin() as conn:
        print("Recreating database tables...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        random.seed(42)
        today = date.today()

        # ========================================================
        # 1. GYM A — FitCore Fitness, Chennai
        # ========================================================
        print("\n--- Seeding Gym A: FitCore Fitness (Chennai) ---")
        gym_a = Gym(name="FitCore Fitness - Anna Nagar")
        session.add(gym_a)
        await session.flush()

        # Users Gym A
        owner_a = User(
            gym_id=gym_a.id,
            email="karthik.ramesh@fitcorefitness.com",
            hashed_password=get_password_hash("FitCore@2026"),
            role="owner",
        )
        staff_a = User(
            gym_id=gym_a.id,
            email="staff@fitcorefitness.com",
            hashed_password=get_password_hash("Staff@2026"),
            role="staff",
        )
        session.add_all([owner_a, staff_a])

        # Plans Gym A
        plan_a_monthly = MembershipPlan(gym_id=gym_a.id, name="Monthly Standard", description="Full facility access, billed monthly", price=1500.0, duration_days=30, status="active")
        plan_a_quarterly = MembershipPlan(gym_id=gym_a.id, name="Quarterly Pro", description="Quarterly access with free locker and functional zone", price=4000.0, duration_days=90, status="active")
        plan_a_annual = MembershipPlan(gym_id=gym_a.id, name="Annual Elite", description="Full year VIP access with personal trainer induction", price=14000.0, duration_days=365, status="active")
        session.add_all([plan_a_monthly, plan_a_quarterly, plan_a_annual])
        await session.flush()
        plans_a = [plan_a_monthly, plan_a_quarterly, plan_a_annual]

        # Trainers Gym A (5 Trainers)
        trainers_a_info = [
            ("Vignesh Sundaram", "vignesh@fitcorefitness.com", "+91 98401 11221", "Strength & Conditioning", 7, "CSCS Certified", "Master Trainer", "Full-time", 25, 4.9, "Former state weightlifter dedicated to functional strength and hypertrophy."),
            ("Priya Natarajan", "priya@fitcorefitness.com", "+91 98402 22332", "CrossFit & HIIT", 5, "CrossFit Level 2", "Senior Trainer", "Full-time", 20, 4.8, "CrossFit specialist helping clients build speed, stamina, and agility."),
            ("Arvind Swaminathan", "arvind@fitcorefitness.com", "+91 98403 33443", "Functional Mobility & Rehab", 4, "ACE Certified", "Trainer", "Part-time", 15, 4.7, "Physio-certified coach helping members train pain-free and fix posture."),
            ("Kavitha Raman", "kavitha@fitcorefitness.com", "+91 98404 44554", "Yoga & Pilates", 6, "RYT 500 Yoga Alliance", "Senior Trainer", "Full-time", 20, 4.9, "Holistic wellness expert blending breathwork, core strength, and mobility."),
            ("Manoj Kumar", "manoj@fitcorefitness.com", "+91 98405 55665", "Bodybuilding & Hypertrophy", 8, "ISSA Certified", "Master Trainer", "Full-time", 25, 4.6, "Dedicated bodybuilding coach specializing in nutrition protocols and muscle gain."),
        ]
        trainers_a = []
        for name, email, phone, spec, exp, cert, lvl, emp, cap, rat, bio in trainers_a_info:
            t = Trainer(
                gym_id=gym_a.id,
                name=name,
                email=email,
                phone=phone,
                specialty=spec,
                years_of_experience=exp,
                certification=cert,
                certification_level=lvl,
                joining_date=today - timedelta(days=365),
                employment_type=emp,
                status="active",
                max_client_capacity=cap,
                rating=rat,
                bio=bio,
            )
            session.add(t)
            trainers_a.append(t)
        await session.flush()

        # Seed 75 Members for Gym A
        # Demographics breakdown: ~55% Male, ~38% Female, ~4% Other, ~3% Prefer not to say
        # Diverse Age groups: <18 (4), 18-24 (15), 25-34 (32), 35-44 (14), 45-54 (7), 55+ (3)
        members_a = []
        age_ranges = [
            (16, 17, 4),    # <18
            (19, 24, 15),   # 18-24
            (25, 34, 32),   # 25-34 (core segment)
            (35, 44, 14),   # 35-44
            (45, 54, 7),    # 45-54
            (55, 66, 3),    # 55+
        ]

        # Generate target ages
        target_ages = []
        for min_a, max_a, count in age_ranges:
            for _ in range(count):
                target_ages.append(random.randint(min_a, max_a))
        random.shuffle(target_ages)

        used_emails = set()

        for i in range(75):
            age = target_ages[i]
            dob_year = today.year - age
            dob_month = random.randint(1, 12)
            dob_day = random.randint(1, 28)
            dob = date(dob_year, dob_month, dob_day)

            # Gender selection
            r_gen = random.random()
            if r_gen < 0.55:
                gender = "Male"
                fname = random.choice(FIRST_NAMES_MALE)
            elif r_gen < 0.93:
                gender = "Female"
                fname = random.choice(FIRST_NAMES_FEMALE)
            elif r_gen < 0.97:
                gender = "Other"
                fname = random.choice(FIRST_NAMES_MALE + FIRST_NAMES_FEMALE)
            else:
                gender = "Prefer not to say"
                fname = random.choice(FIRST_NAMES_MALE + FIRST_NAMES_FEMALE)

            lname = random.choice(LAST_NAMES)
            full_name = f"{fname} {lname}"
            email_slug = f"{fname.lower()}.{lname.lower()}{i+1}@example.com"
            while email_slug in used_emails:
                email_slug = f"{fname.lower()}.{lname.lower()}{random.randint(100, 9999)}@example.com"
            used_emails.add(email_slug)

            phone = f"+91 {random.randint(90000, 99999)} {random.randint(10000, 99999)}"
            join_offset = random.randint(15, 300)
            join_dt = today - timedelta(days=join_offset)

            assigned_trainer = random.choice(trainers_a) if random.random() < 0.85 else None

            m = Member(
                gym_id=gym_a.id,
                name=full_name,
                first_name=fname,
                last_name=lname,
                email=email_slug,
                phone=phone,
                date_of_birth=dob,
                gender=gender,
                occupation=random.choice(OCCUPATIONS),
                city="Chennai",
                emergency_contact_name=f"{random.choice(FIRST_NAMES_MALE)} {lname}",
                emergency_contact_phone=f"+91 98400 {random.randint(10000, 99999)}",
                join_date=join_dt,
                preferred_training_time=random.choice(TRAINING_TIMES),
                fitness_goal=random.choice(FITNESS_GOALS),
                acquisition_source=random.choice(ACQ_SOURCES),
                referral_source="Friend" if random.random() < 0.3 else None,
                trainer_id=assigned_trainer.id if assigned_trainer else None,
                status="active",
            )
            session.add(m)
            members_a.append(m)

        await session.flush()
        print(f"Created {len(members_a)} members for Gym A.")

        # Seed Trainer-Member Assignments for Gym A
        for m in members_a:
            if m.trainer_id:
                assign = TrainerMemberAssignment(
                    gym_id=gym_a.id,
                    trainer_id=m.trainer_id,
                    member_id=m.id,
                    assigned_at=datetime.combine(m.join_date, datetime.min.time()).replace(tzinfo=timezone.utc),
                    status="active",
                )
                session.add(assign)
        await session.flush()

        # Seed Trainer Reviews for Gym A
        SAMPLE_REVIEWS = [
            "Fantastic coach! Really helped improve my deadlift technique and posture.",
            "Very motivating and attentive to form and recovery during every session.",
            "Great workout routine, custom diet guidance really accelerated results.",
            "Super knowledgeable and punctual. Pushes me past plateaus safely.",
            "Clear instructions and friendly demeanor. Highly recommend for all fitness levels.",
            "Focuses on functional movements and injury prevention. Excellent trainer.",
        ]
        for t in trainers_a:
            t_mems = [m for m in members_a if m.trainer_id == t.id]
            sample_mems = t_mems[:min(len(t_mems), random.randint(3, 5))]
            for sm in sample_mems:
                rev = TrainerReview(
                    gym_id=gym_a.id,
                    trainer_id=t.id,
                    member_id=sm.id,
                    rating=random.choice([4, 5, 5, 5, 4, 5]),
                    review=random.choice(SAMPLE_REVIEWS),
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(2, 45)),
                )
                session.add(rev)
        await session.flush()

        # Create Memberships and Payments for Gym A
        # ~52 active members, ~15 expired/churned, ~8 expiring within 7 days (at-risk)
        all_payments_a = []

        for idx, m in enumerate(members_a):
            chosen_plan = random.choice(plans_a)

            if idx < 48:
                # Active healthy membership
                start_offset = random.randint(5, 60)
                m_start = today - timedelta(days=start_offset)
                m_end = m_start + timedelta(days=chosen_plan.duration_days)
                if m_end <= today:
                    m_end = today + timedelta(days=random.randint(10, 45))

                mship = Membership(
                    gym_id=gym_a.id,
                    member_id=m.id,
                    plan_id=chosen_plan.id,
                    start_date=m_start,
                    end_date=m_end,
                    status="active",
                )
                session.add(mship)
                await session.flush()

                # Paid payment
                pmt_dt = datetime.combine(m_start, datetime.min.time()).replace(tzinfo=timezone.utc)
                pmt = Payment(
                    gym_id=gym_a.id,
                    member_id=m.id,
                    membership_id=mship.id,
                    amount=chosen_plan.price,
                    paid_at=pmt_dt,
                    status="paid",
                )
                session.add(pmt)
                all_payments_a.append(pmt)

                # Add historical renewals for older members (idx < 20)
                if idx < 20 and m.join_date < today - timedelta(days=90):
                    past_start = m_start - timedelta(days=chosen_plan.duration_days)
                    past_end = m_start - timedelta(days=1)
                    past_mship = Membership(
                        gym_id=gym_a.id,
                        member_id=m.id,
                        plan_id=chosen_plan.id,
                        start_date=past_start,
                        end_date=past_end,
                        status="expired",
                    )
                    session.add(past_mship)
                    await session.flush()
                    past_pmt_dt = datetime.combine(past_start, datetime.min.time()).replace(tzinfo=timezone.utc)
                    session.add(Payment(
                        gym_id=gym_a.id,
                        member_id=m.id,
                        membership_id=past_mship.id,
                        amount=chosen_plan.price,
                        paid_at=past_pmt_dt,
                        status="paid",
                    ))

            elif idx < 56:
                # At-risk (Expiring within 1-7 days)
                days_left = random.randint(1, 6)
                m_end = today + timedelta(days=days_left)
                m_start = m_end - timedelta(days=chosen_plan.duration_days)

                mship = Membership(
                    gym_id=gym_a.id,
                    member_id=m.id,
                    plan_id=chosen_plan.id,
                    start_date=m_start,
                    end_date=m_end,
                    status="active",
                )
                session.add(mship)
                await session.flush()

                pmt_dt = datetime.combine(m_start, datetime.min.time()).replace(tzinfo=timezone.utc)
                pmt = Payment(
                    gym_id=gym_a.id,
                    member_id=m.id,
                    membership_id=mship.id,
                    amount=chosen_plan.price,
                    paid_at=pmt_dt,
                    status="paid",
                )
                session.add(pmt)
                all_payments_a.append(pmt)

            elif idx < 60:
                # At-risk via unresolved failed payment
                m_start = today - timedelta(days=15)
                m_end = m_start + timedelta(days=chosen_plan.duration_days)
                mship = Membership(
                    gym_id=gym_a.id,
                    member_id=m.id,
                    plan_id=chosen_plan.id,
                    start_date=m_start,
                    end_date=m_end,
                    status="active",
                )
                session.add(mship)
                await session.flush()

                failed_dt = datetime.combine(today - timedelta(days=random.randint(2, 10)), datetime.min.time()).replace(tzinfo=timezone.utc)
                pmt = Payment(
                    gym_id=gym_a.id,
                    member_id=m.id,
                    membership_id=mship.id,
                    amount=chosen_plan.price,
                    paid_at=failed_dt,
                    status="failed",
                )
                session.add(pmt)
                all_payments_a.append(pmt)

            else:
                # Expired / Inactive members
                m.status = "inactive"
                expired_days_ago = random.randint(10, 80)
                m_end = today - timedelta(days=expired_days_ago)
                m_start = m_end - timedelta(days=chosen_plan.duration_days)

                mship = Membership(
                    gym_id=gym_a.id,
                    member_id=m.id,
                    plan_id=chosen_plan.id,
                    start_date=m_start,
                    end_date=m_end,
                    status="expired",
                )
                session.add(mship)
                await session.flush()

                pmt_dt = datetime.combine(m_start, datetime.min.time()).replace(tzinfo=timezone.utc)
                pmt = Payment(
                    gym_id=gym_a.id,
                    member_id=m.id,
                    membership_id=mship.id,
                    amount=chosen_plan.price,
                    paid_at=pmt_dt,
                    status="paid",
                )
                session.add(pmt)
                all_payments_a.append(pmt)

        await session.commit()
        print("Memberships and payments successfully committed for Gym A.")

        # Compute 90 days of realistic daily summary metrics for Gym A
        print("Generating 90 days of deterministic summary_metrics for Gym A...")
        for day_offset in range(90, -1, -1):
            target_d = today - timedelta(days=day_offset)
            act_m = await calculate_active_members(session, gym_a.id, target_d)
            mrr_d = await calculate_mrr(session, gym_a.id, target_d)
            ren_d = await calculate_renewal_rate(session, gym_a.id, target_d, window_days=30)
            risk_d, _ = await get_at_risk_members_data(session, gym_a.id, target_d)

            metric_row = SummaryMetric(
                gym_id=gym_a.id,
                metric_date=target_d,
                active_members=act_m,
                mrr=mrr_d,
                renewal_rate=ren_d,
                at_risk_count=risk_d,
                new_members=random.randint(0, 2),
                churned_members=random.randint(0, 1),
            )
            session.add(metric_row)

        await session.commit()
        print("90 days of summary metrics saved for Gym A.")

        # ========================================================
        # 2. GYM B — Urban Strength Club, Coimbatore
        # ========================================================
        print("\n--- Seeding Gym B: Urban Strength Club (Coimbatore) ---")
        gym_b = Gym(name="Urban Strength Club - RS Puram")
        session.add(gym_b)
        await session.flush()

        # Users Gym B
        owner_b = User(
            gym_id=gym_b.id,
            email="arjun.kumar@urbanstrength.in",
            hashed_password=get_password_hash("Urban@2026"),
            role="owner",
        )
        staff_b = User(
            gym_id=gym_b.id,
            email="staff@urbanstrength.in",
            hashed_password=get_password_hash("UrbanStaff@2026"),
            role="staff",
        )
        session.add_all([owner_b, staff_b])

        # Plans Gym B
        plan_b_monthly = MembershipPlan(gym_id=gym_b.id, name="Power Monthly", description="All equipment access with flexible monthly billing", price=1800.0, duration_days=30, status="active")
        plan_b_quarterly = MembershipPlan(gym_id=gym_b.id, name="Strength 3-Month", description="Targeted strength cycles with functional coaching", price=4800.0, duration_days=90, status="active")
        plan_b_annual = MembershipPlan(gym_id=gym_b.id, name="Titan Annual", description="Complete athlete package with sauna and premium access", price=16500.0, duration_days=365, status="active")
        session.add_all([plan_b_monthly, plan_b_quarterly, plan_b_annual])
        await session.flush()
        plans_b = [plan_b_monthly, plan_b_quarterly, plan_b_annual]

        # Trainers Gym B (3 Trainers)
        trainers_b_info = [
            ("Ranjith Naidu", "ranjith@urbanstrength.in", "+91 94431 11221", "Powerlifting & Barbell", 6, "IPF Coach", "Senior Coach", "Full-time", 20, 4.8, "Competitive powerlifter coaching squat, bench, and deadlift mechanics."),
            ("Divya Sridhar", "divya@urbanstrength.in", "+91 94432 22332", "Athletic Conditioning", 4, "ACE Certified", "Coach", "Full-time", 18, 4.7, "Specialist in high-intensity stamina, agility training, and endurance."),
            ("Siddharth Chettiar", "siddharth@urbanstrength.in", "+91 94433 33443", "Mobility & Calisthenics", 5, "Calisthenics Level 2", "Coach", "Part-time", 15, 4.9, "Bodyweight movement master focusing on handstands, muscle-ups, and joint health."),
        ]
        trainers_b = []
        for name, email, phone, spec, exp, cert, lvl, emp, cap, rat, bio in trainers_b_info:
            t = Trainer(
                gym_id=gym_b.id,
                name=name,
                email=email,
                phone=phone,
                specialty=spec,
                years_of_experience=exp,
                certification=cert,
                certification_level=lvl,
                joining_date=today - timedelta(days=200),
                employment_type=emp,
                status="active",
                max_client_capacity=cap,
                rating=rat,
                bio=bio,
            )
            session.add(t)
            trainers_b.append(t)
        await session.flush()

        # Seed 45 Members for Gym B
        members_b = []
        target_ages_b = []
        age_ranges_b = [
            (17, 17, 2),
            (19, 24, 10),
            (25, 34, 20),
            (35, 44, 9),
            (45, 54, 3),
            (55, 62, 1),
        ]
        for min_a, max_a, count in age_ranges_b:
            for _ in range(count):
                target_ages_b.append(random.randint(min_a, max_a))
        random.shuffle(target_ages_b)

        for i in range(45):
            age = target_ages_b[i]
            dob = date(today.year - age, random.randint(1, 12), random.randint(1, 28))

            r_gen = random.random()
            if r_gen < 0.60:
                gender = "Male"
                fname = random.choice(FIRST_NAMES_MALE)
            elif r_gen < 0.95:
                gender = "Female"
                fname = random.choice(FIRST_NAMES_FEMALE)
            else:
                gender = "Other"
                fname = random.choice(FIRST_NAMES_MALE)

            lname = random.choice(LAST_NAMES)
            full_name = f"{fname} {lname}"
            email_b = f"{fname.lower()}.{lname.lower()}{i+100}@urbanstrength.in"
            phone_b = f"+91 9443{random.randint(100000, 999999)}"
            join_dt = today - timedelta(days=random.randint(5, 75))

            assigned_trainer = trainers_b[i % len(trainers_b)]

            m = Member(
                gym_id=gym_b.id,
                name=full_name,
                first_name=fname,
                last_name=lname,
                email=email_b,
                phone=phone_b,
                date_of_birth=dob,
                gender=gender,
                occupation=random.choice(OCCUPATIONS),
                city="Coimbatore",
                emergency_contact_name=f"{random.choice(FIRST_NAMES_MALE)} {lname}",
                emergency_contact_phone=f"+91 94430 {random.randint(10000, 99999)}",
                join_date=join_dt,
                preferred_training_time=random.choice(TRAINING_TIMES),
                fitness_goal=random.choice(FITNESS_GOALS),
                acquisition_source=random.choice(ACQ_SOURCES),
                referral_source=None,
                trainer_id=assigned_trainer.id,
                status="active",
            )
            session.add(m)
            members_b.append(m)

        await session.flush()
        print(f"Created {len(members_b)} members for Gym B.")

        # Seed Trainer-Member Assignments for Gym B
        for m in members_b:
            if m.trainer_id:
                assign = TrainerMemberAssignment(
                    gym_id=gym_b.id,
                    trainer_id=m.trainer_id,
                    member_id=m.id,
                    assigned_at=datetime.combine(m.join_date, datetime.min.time()).replace(tzinfo=timezone.utc),
                    status="active",
                )
                session.add(assign)
        await session.flush()

        # Seed Trainer Reviews for Gym B
        for t in trainers_b:
            t_mems = [m for m in members_b if m.trainer_id == t.id]
            sample_mems = t_mems[:min(len(t_mems), random.randint(2, 4))]
            for sm in sample_mems:
                rev = TrainerReview(
                    gym_id=gym_b.id,
                    trainer_id=t.id,
                    member_id=sm.id,
                    rating=random.choice([4, 5, 5, 4]),
                    review=random.choice(SAMPLE_REVIEWS),
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(3, 40)),
                )
                session.add(rev)
        await session.flush()

        # Memberships & Payments for Gym B
        for idx, m in enumerate(members_b):
            chosen_plan = random.choice(plans_b)
            if idx < 32:
                # Active
                m_start = today - timedelta(days=random.randint(5, 50))
                m_end = m_start + timedelta(days=chosen_plan.duration_days)
                if m_end <= today:
                    m_end = today + timedelta(days=random.randint(15, 60))
                mship = Membership(
                    gym_id=gym_b.id,
                    member_id=m.id,
                    plan_id=chosen_plan.id,
                    start_date=m_start,
                    end_date=m_end,
                    status="active",
                )
                session.add(mship)
                await session.flush()
                session.add(Payment(
                    gym_id=gym_b.id,
                    member_id=m.id,
                    membership_id=mship.id,
                    amount=chosen_plan.price,
                    paid_at=datetime.combine(m_start, datetime.min.time()).replace(tzinfo=timezone.utc),
                    status="paid",
                ))
            elif idx < 37:
                # Expiring in 4 days (At-risk)
                m_end = today + timedelta(days=random.randint(2, 5))
                m_start = m_end - timedelta(days=chosen_plan.duration_days)
                mship = Membership(
                    gym_id=gym_b.id,
                    member_id=m.id,
                    plan_id=chosen_plan.id,
                    start_date=m_start,
                    end_date=m_end,
                    status="active",
                )
                session.add(mship)
                await session.flush()
                session.add(Payment(
                    gym_id=gym_b.id,
                    member_id=m.id,
                    membership_id=mship.id,
                    amount=chosen_plan.price,
                    paid_at=datetime.combine(m_start, datetime.min.time()).replace(tzinfo=timezone.utc),
                    status="paid",
                ))
            else:
                # Inactive / expired
                m.status = "inactive"
                m_end = today - timedelta(days=random.randint(5, 45))
                m_start = m_end - timedelta(days=chosen_plan.duration_days)
                mship = Membership(
                    gym_id=gym_b.id,
                    member_id=m.id,
                    plan_id=chosen_plan.id,
                    start_date=m_start,
                    end_date=m_end,
                    status="expired",
                )
                session.add(mship)
                await session.flush()
                session.add(Payment(
                    gym_id=gym_b.id,
                    member_id=m.id,
                    membership_id=mship.id,
                    amount=chosen_plan.price,
                    paid_at=datetime.combine(m_start, datetime.min.time()).replace(tzinfo=timezone.utc),
                    status="paid",
                ))

        await session.commit()

        # Compute 90 days of metrics for Gym B
        print("Generating 90 days of summary_metrics for Gym B...")
        for day_offset in range(90, -1, -1):
            target_d = today - timedelta(days=day_offset)
            act_m = await calculate_active_members(session, gym_b.id, target_d)
            mrr_d = await calculate_mrr(session, gym_b.id, target_d)
            ren_d = await calculate_renewal_rate(session, gym_b.id, target_d, window_days=30)
            risk_d, _ = await get_at_risk_members_data(session, gym_b.id, target_d)

            metric_row = SummaryMetric(
                gym_id=gym_b.id,
                metric_date=target_d,
                active_members=act_m,
                mrr=mrr_d,
                renewal_rate=ren_d,
                at_risk_count=risk_d,
                new_members=random.randint(0, 1),
                churned_members=0,
            )
            session.add(metric_row)

        await session.commit()
        print("90 days of summary metrics saved for Gym B.")

        print("\n========================================================")
        print("FITFLOW SEEDING COMPLETE!")
        print("Gym A (FitCore Fitness, Chennai):")
        print("  Owner Login: karthik.ramesh@fitcorefitness.com / FitCore@2026")
        print("  Members: 75 | Trainers: 5 | Plans: 3")
        print("Gym B (Urban Strength Club, Coimbatore):")
        print("  Owner Login: arjun.kumar@urbanstrength.in / Urban@2026")
        print("  Members: 45 | Trainers: 3 | Plans: 3")
        print("========================================================\n")


if __name__ == "__main__":
    asyncio.run(seed_data())
