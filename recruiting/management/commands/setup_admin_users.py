"""
Management command to set up admin users for RecruitApp.

Usage:
    python manage.py setup_admin_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from recruiting.models import UserProfile, FamilyAccount, FamilyMember, AdminSettings


class Command(BaseCommand):
    help = 'Creates admin users for RecruitApp (johnb, dmarlo, jackwaddey)'

    def handle(self, *args, **options):
        """Create or update admin users with appropriate permissions."""

        admin_users = [
            {
                'username': 'johnb',
                'email': 'dev@hackworthai.com',
                'first_name': 'John',
                'last_name': 'B',
                'is_superuser': True,
                'is_staff': True,
                'password': 'RecruitApp2024!',  # Change this after first login
            },
            {
                'username': 'dmarlo',
                'email': 'dmarlo@gmail.com',
                'first_name': 'David',
                'last_name': 'Marlo',
                'is_superuser': False,
                'is_staff': True,
                'password': 'RecruitApp2024!',  # Change this after first login
            },
            {
                'username': 'jackwaddey',
                'email': 'jackwaddey@me.com',
                'first_name': 'Jack',
                'last_name': 'Waddey',
                'is_superuser': False,
                'is_staff': True,
                'password': 'RecruitApp2024!',  # Change this after first login
            },
        ]

        self.stdout.write(self.style.SUCCESS('Creating admin users...'))

        for user_data in admin_users:
            username = user_data['username']
            email = user_data['email']
            password = user_data.pop('password')

            # Create or update user
            user, created = User.objects.get_or_create(
                username=username,
                defaults=user_data
            )

            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {username} ({email})')
                )
            else:
                # Update existing user
                for key, value in user_data.items():
                    setattr(user, key, value)
                user.save()
                self.stdout.write(
                    self.style.WARNING(f'Updated existing user: {username} ({email})')
                )

            # Create UserProfile if it doesn't exist
            user_profile, profile_created = UserProfile.objects.get_or_create(
                user=user
            )
            if profile_created:
                self.stdout.write(f'  - Created UserProfile for {username}')

            # Create FamilyAccount if it doesn't exist
            family_account, family_created = FamilyAccount.objects.get_or_create(
                primary_email=email,
                defaults={'subscription_tier': 'elite'}  # Admins get elite tier
            )
            if family_created:
                self.stdout.write(f'  - Created FamilyAccount for {email}')

            # Create FamilyMember if it doesn't exist
            family_member, member_created = FamilyMember.objects.get_or_create(
                user=user,
                defaults={
                    'family_account': family_account,
                    'role': 'parent',  # Admins are treated as parents for permissions
                    'can_invite_members': True,
                    'can_edit_profile': True,
                    'can_manage_ledger': True,
                    'can_manage_actions': True,
                }
            )
            if member_created:
                self.stdout.write(f'  - Created FamilyMember for {username}')

            # Create AdminSettings if it doesn't exist
            admin_settings, admin_created = AdminSettings.objects.get_or_create(
                user=user,
                defaults={
                    'untethered_mode_enabled': False,
                    'can_view_all_user_data': True,
                    'can_reset_own_data': True,
                    'can_reset_any_user_data': (username == 'johnb'),  # Only superuser
                    'can_modify_prompts': True,
                }
            )
            if admin_created:
                self.stdout.write(f'  - Created AdminSettings for {username}')
            else:
                # Update permissions
                admin_settings.can_view_all_user_data = True
                admin_settings.can_reset_own_data = True
                admin_settings.can_reset_any_user_data = (username == 'johnb')
                admin_settings.can_modify_prompts = True
                admin_settings.save()
                self.stdout.write(f'  - Updated AdminSettings for {username}')

        self.stdout.write('\n')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Admin users setup complete!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('\nLogin credentials (CHANGE PASSWORDS AFTER FIRST LOGIN):')
        self.stdout.write('  • johnb (SUPERUSER): dev@hackworthai.com')
        self.stdout.write('  • dmarlo (Admin): dmarlo@gmail.com')
        self.stdout.write('  • jackwaddey (Admin): jackwaddey@me.com')
        self.stdout.write('  • Default password: RecruitApp2024!')
        self.stdout.write('\nPermissions:')
        self.stdout.write('  • johnb: Full superuser access + can reset any user data')
        self.stdout.write('  • dmarlo: Staff access + view all data + modify prompts')
        self.stdout.write('  • jackwaddey: Staff access + view all data + modify prompts')
        self.stdout.write('\n')
