"""
Django management command for fixing admin assets
"""

from django.core.management.base import BaseCommand
from faktury.services.admin_asset_manager import AdminAssetManager


class Command(BaseCommand):
    """Django management command for admin asset management"""
    
    help = 'Fix Django admin static assets and styling issues'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='Check admin asset status without making changes'
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix all admin asset issues automatically'
        )
        parser.add_argument(
            '--download',
            action='store_true',
            help='Download missing admin assets'
        )
        parser.add_argument(
            '--configure',
            action='store_true',
            help='Configure admin theme only'
        )
    
    def handle(self, *args, **options):
        manager = AdminAssetManager()
        
        if options['check']:
            self.stdout.write(self.style.HTTP_INFO('Checking admin asset status...'))
            report = manager.get_asset_status_report()
            
            self.stdout.write(f"\n📊 Asset Status Report:")
            self.stdout.write(f"Total required assets: {report['total_required_assets']}")
            self.stdout.write(f"Missing assets: {report['missing_assets_count']}")
            
            if report['missing_assets']:
                self.stdout.write(self.style.WARNING("\n❌ Missing files:"))
                for asset in report['missing_assets']:
                    self.stdout.write(f"  - {asset}")
            else:
                self.stdout.write(self.style.SUCCESS("\n✅ All required assets found"))
            
            self.stdout.write(f"\n🔍 Validation Results:")
            for check, result in report['validation_results'].items():
                status = self.style.SUCCESS("✓") if result else self.style.ERROR("✗")
                self.stdout.write(f"  {status} {check.replace('_', ' ').title()}")
            
            if report['recommendations']:
                self.stdout.write(f"\n💡 Recommendations:")
                for rec in report['recommendations']:
                    self.stdout.write(f"  - {rec}")
        
        elif options['fix']:
            self.stdout.write(self.style.HTTP_INFO('Fixing all admin asset issues...'))
            report = manager.fix_all_assets()
            
            if report['success']:
                self.stdout.write(
                    self.style.SUCCESS('\n✅ Admin assets fixed successfully!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('\n⚠️  Admin assets fixed with some issues')
                )
            
            self.stdout.write(f"\n📈 Results:")
            self.stdout.write(f"  Missing assets found: {report['missing_assets_found']}")
            self.stdout.write(f"  Assets downloaded: {report['assets_downloaded']}")
            
            if report['download_failures'] > 0:
                self.stdout.write(
                    self.style.WARNING(f"  Download failures: {report['download_failures']}")
                )
            
            self.stdout.write(f"  Theme configured: {'✅' if report['theme_configured'] else '❌'}")
            
            # Show validation results
            self.stdout.write(f"\n🔍 Final Validation:")
            for check, result in report['validation_results'].items():
                status = "✅" if result else "❌"
                self.stdout.write(f"  {status} {check.replace('_', ' ').title()}")
        
        elif options['download']:
            self.stdout.write(self.style.HTTP_INFO('Downloading missing admin assets...'))
            missing = manager.collect_missing_assets()
            
            if missing:
                self.stdout.write(f"Found {len(missing)} missing assets")
                results = manager.download_admin_assets()
                success_count = sum(1 for success in results.values() if success)
                
                if success_count == len(missing):
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Downloaded all {success_count} assets successfully")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  Downloaded {success_count}/{len(missing)} assets")
                    )
                    
                    # Show failed downloads
                    failed = [asset for asset, success in results.items() if not success]
                    if failed:
                        self.stdout.write(self.style.ERROR("Failed downloads:"))
                        for asset in failed:
                            self.stdout.write(f"  - {asset}")
            else:
                self.stdout.write(self.style.SUCCESS("✅ No missing assets found"))
        
        elif options['configure']:
            self.stdout.write(self.style.HTTP_INFO('Configuring admin theme...'))
            manager.configure_admin_theme()
            self.stdout.write(self.style.SUCCESS("✅ Admin theme configured successfully"))
        
        else:
            self.stdout.write(self.style.HTTP_INFO('Django Admin Asset Manager'))
            self.stdout.write('Available options:')
            self.stdout.write('  --check      Check admin asset status')
            self.stdout.write('  --fix        Fix all admin asset issues')
            self.stdout.write('  --download   Download missing assets only')
            self.stdout.write('  --configure  Configure theme only')
            self.stdout.write('\nExample: python manage.py fix_admin_assets --fix')