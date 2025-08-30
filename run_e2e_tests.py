#!/usr/bin/env python3
"""
Główny skrypt do uruchamiania wszystkich testów E2E dla FaktuLove
Uruchamia testy Selenium, Playwright i Cypress w skoordynowany sposób
"""

import os
import sys
import time
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class E2ETestOrchestrator:
    """Orkiestrator wszystkich testów E2E"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'base_url': base_url,
            'test_suites': {},
            'summary': {
                'total_suites': 0,
                'passed_suites': 0,
                'failed_suites': 0,
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0
            }
        }
        
    def run_all_tests(self):
        """Uruchom wszystkie testy E2E"""
        print("🚀 Uruchamianie kompleksowych testów E2E dla FaktuLove")
        print(f"🎯 Testowany URL: {self.base_url}")
        print(f"⏰ Czas rozpoczęcia: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Sprawdź czy serwer jest dostępny
        if not self._check_server_availability():
            print("❌ Serwer nie jest dostępny. Sprawdź czy aplikacja działa.")
            return False
            
        # Uruchom testy w kolejności
        test_suites = [
            ('Comprehensive Application Tests', self._run_comprehensive_tests),
            ('Selenium Tests', self._run_selenium_tests),
            ('Playwright Tests', self._run_playwright_tests),
            ('Cypress Tests', self._run_cypress_tests),
            ('API Tests', self._run_api_tests)
        ]
        
        for suite_name, test_func in test_suites:
            print(f"\n🧪 Uruchamianie: {suite_name}")
            print("-" * 60)
            
            try:
                result = test_func()
                self.results['test_suites'][suite_name] = result
                self.results['summary']['total_suites'] += 1
                
                if result['success']:
                    self.results['summary']['passed_suites'] += 1
                    print(f"✅ {suite_name} - ZAKOŃCZONE POMYŚLNIE")
                else:
                    self.results['summary']['failed_suites'] += 1
                    print(f"❌ {suite_name} - NIEPOWODZENIE")
                    
                # Aktualizuj statystyki testów
                if 'tests' in result:
                    self.results['summary']['total_tests'] += result['tests'].get('total', 0)
                    self.results['summary']['passed_tests'] += result['tests'].get('passed', 0)
                    self.results['summary']['failed_tests'] += result['tests'].get('failed', 0)
                    
            except Exception as e:
                print(f"💥 {suite_name} - BŁĄD: {str(e)}")
                self.results['test_suites'][suite_name] = {
                    'success': False,
                    'error': str(e),
                    'duration': 0
                }
                self.results['summary']['failed_suites'] += 1
                
        # Generuj raport końcowy
        self._generate_final_report()
        
        return self.results['summary']['failed_suites'] == 0
        
    def _check_server_availability(self) -> bool:
        """Sprawdź dostępność serwera"""
        try:
            import requests
            response = requests.get(self.base_url, timeout=10)
            return response.status_code < 500
        except Exception as e:
            print(f"⚠️ Nie można połączyć się z serwerem: {e}")
            return False
            
    def _run_comprehensive_tests(self) -> Dict[str, Any]:
        """Uruchom kompleksowe testy aplikacji"""
        start_time = time.time()
        
        try:
            # Uruchom kompleksowy test aplikacji
            result = subprocess.run([
                sys.executable, 'tests/e2e/test_comprehensive_application.py',
                '--url', self.base_url
            ], capture_output=True, text=True, timeout=300)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                # Spróbuj wyciągnąć statystyki z outputu
                output_lines = result.stdout.split('\n')
                stats = self._extract_test_stats(output_lines)
                
                return {
                    'success': True,
                    'duration': duration,
                    'output': result.stdout,
                    'tests': stats
                }
            else:
                return {
                    'success': False,
                    'duration': duration,
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'duration': time.time() - start_time,
                'error': 'Test timeout (5 minutes)'
            }
        except Exception as e:
            return {
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
            
    def _run_selenium_tests(self) -> Dict[str, Any]:
        """Uruchom testy Selenium"""
        start_time = time.time()
        
        try:
            # Sprawdź czy plik testów Selenium istnieje
            selenium_test_file = 'tests/e2e/selenium_ocr_tests.py'
            if not os.path.exists(selenium_test_file):
                return {
                    'success': False,
                    'duration': 0,
                    'error': f'Plik testów Selenium nie istnieje: {selenium_test_file}'
                }
                
            result = subprocess.run([
                sys.executable, selenium_test_file,
                '--url', self.base_url
            ], capture_output=True, text=True, timeout=600)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                stats = self._extract_test_stats(result.stdout.split('\n'))
                return {
                    'success': True,
                    'duration': duration,
                    'output': result.stdout,
                    'tests': stats
                }
            else:
                return {
                    'success': False,
                    'duration': duration,
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'duration': time.time() - start_time,
                'error': 'Selenium tests timeout (10 minutes)'
            }
        except Exception as e:
            return {
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
            
    def _run_playwright_tests(self) -> Dict[str, Any]:
        """Uruchom testy Playwright"""
        start_time = time.time()
        
        try:
            # Sprawdź czy Playwright jest zainstalowany
            try:
                import playwright
            except ImportError:
                return {
                    'success': False,
                    'duration': 0,
                    'error': 'Playwright nie jest zainstalowany. Uruchom: pip install playwright && playwright install'
                }
                
            result = subprocess.run([
                sys.executable, 'tests/e2e/playwright_tests.py',
                '--url', self.base_url
            ], capture_output=True, text=True, timeout=600)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                stats = self._extract_test_stats(result.stdout.split('\n'))
                return {
                    'success': True,
                    'duration': duration,
                    'output': result.stdout,
                    'tests': stats
                }
            else:
                return {
                    'success': False,
                    'duration': duration,
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'duration': time.time() - start_time,
                'error': 'Playwright tests timeout (10 minutes)'
            }
        except Exception as e:
            return {
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
            
    def _run_cypress_tests(self) -> Dict[str, Any]:
        """Uruchom testy Cypress"""
        start_time = time.time()
        
        try:
            # Sprawdź czy Cypress jest dostępny
            cypress_check = subprocess.run(['npx', 'cypress', '--version'], 
                                         capture_output=True, text=True)
            
            if cypress_check.returncode != 0:
                return {
                    'success': False,
                    'duration': 0,
                    'error': 'Cypress nie jest zainstalowany. Uruchom: npm install cypress'
                }
                
            # Ustaw zmienną środowiskową dla Cypress
            env = os.environ.copy()
            env['CYPRESS_BASE_URL'] = self.base_url
            
            result = subprocess.run([
                'npx', 'cypress', 'run',
                '--spec', 'tests/e2e/cypress_tests.js',
                '--headless'
            ], capture_output=True, text=True, timeout=600, env=env)
            
            duration = time.time() - start_time
            
            # Cypress zwraca 0 dla sukcesu
            success = result.returncode == 0
            
            return {
                'success': success,
                'duration': duration,
                'output': result.stdout,
                'error': result.stderr if not success else None,
                'tests': self._extract_cypress_stats(result.stdout)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'duration': time.time() - start_time,
                'error': 'Cypress tests timeout (10 minutes)'
            }
        except Exception as e:
            return {
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
            
    def _run_api_tests(self) -> Dict[str, Any]:
        """Uruchom testy API"""
        start_time = time.time()
        
        try:
            import requests
            
            # Podstawowe testy API
            endpoints = [
                ('/', 'Homepage'),
                ('/admin/', 'Admin Panel'),
                ('/api/', 'API Root'),
                ('/static/admin/css/base.css', 'Static CSS'),
            ]
            
            results = []
            for endpoint, name in endpoints:
                try:
                    url = f"{self.base_url}{endpoint}"
                    response = requests.get(url, timeout=10)
                    
                    results.append({
                        'name': name,
                        'url': url,
                        'status_code': response.status_code,
                        'success': response.status_code < 500,
                        'response_time': response.elapsed.total_seconds()
                    })
                    
                except Exception as e:
                    results.append({
                        'name': name,
                        'url': f"{self.base_url}{endpoint}",
                        'success': False,
                        'error': str(e)
                    })
                    
            duration = time.time() - start_time
            passed = sum(1 for r in results if r['success'])
            total = len(results)
            
            return {
                'success': passed == total,
                'duration': duration,
                'results': results,
                'tests': {
                    'total': total,
                    'passed': passed,
                    'failed': total - passed
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
            
    def _extract_test_stats(self, output_lines: List[str]) -> Dict[str, int]:
        """Wyciągnij statystyki testów z outputu"""
        stats = {'total': 0, 'passed': 0, 'failed': 0}
        
        for line in output_lines:
            line = line.strip()
            
            # Szukaj wzorców statystyk
            if 'Total Tests:' in line:
                try:
                    stats['total'] = int(line.split(':')[1].strip())
                except:
                    pass
                    
            elif 'Passed:' in line:
                try:
                    stats['passed'] = int(line.split(':')[1].strip().split()[0])
                except:
                    pass
                    
            elif 'Failed:' in line:
                try:
                    stats['failed'] = int(line.split(':')[1].strip().split()[0])
                except:
                    pass
                    
            # Alternatywne wzorce
            elif '✅' in line and 'PASSED' in line:
                stats['passed'] += 1
                stats['total'] += 1
            elif '❌' in line and ('FAILED' in line or 'ERROR' in line):
                stats['failed'] += 1
                stats['total'] += 1
                
        return stats
        
    def _extract_cypress_stats(self, output: str) -> Dict[str, int]:
        """Wyciągnij statystyki z outputu Cypress"""
        stats = {'total': 0, 'passed': 0, 'failed': 0}
        
        # Cypress ma specyficzny format outputu
        lines = output.split('\n')
        for line in lines:
            if 'passing' in line:
                try:
                    stats['passed'] = int(line.split()[0])
                except:
                    pass
            elif 'failing' in line:
                try:
                    stats['failed'] = int(line.split()[0])
                except:
                    pass
                    
        stats['total'] = stats['passed'] + stats['failed']
        return stats
        
    def _generate_final_report(self):
        """Generuj końcowy raport"""
        print("\n" + "="*80)
        print("📊 PODSUMOWANIE TESTÓW E2E")
        print("="*80)
        
        summary = self.results['summary']
        
        print(f"🎯 Testowany URL: {self.base_url}")
        print(f"⏰ Czas zakończenia: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n📈 STATYSTYKI OGÓLNE:")
        print(f"   Zestawy testów: {summary['total_suites']}")
        print(f"   Pomyślne: {summary['passed_suites']} ✅")
        print(f"   Niepowodzenia: {summary['failed_suites']} ❌")
        
        if summary['total_tests'] > 0:
            print(f"\n🧪 STATYSTYKI TESTÓW:")
            print(f"   Łączna liczba testów: {summary['total_tests']}")
            print(f"   Pomyślne: {summary['passed_tests']} ✅")
            print(f"   Niepowodzenia: {summary['failed_tests']} ❌")
            print(f"   Wskaźnik sukcesu: {(summary['passed_tests']/summary['total_tests']*100):.1f}%")
            
        print(f"\n📋 SZCZEGÓŁY ZESTAWÓW TESTÓW:")
        for suite_name, result in self.results['test_suites'].items():
            status = "✅" if result['success'] else "❌"
            duration = result.get('duration', 0)
            print(f"   {status} {suite_name} ({duration:.1f}s)")
            
            if not result['success'] and 'error' in result:
                print(f"      Błąd: {result['error']}")
                
        # Zapisz szczegółowy raport JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"e2e_test_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
            
        print(f"\n📄 Szczegółowy raport zapisany: {report_file}")
        
        # Generuj HTML raport
        html_report = self._generate_html_report()
        html_file = f"e2e_test_report_{timestamp}.html"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
            
        print(f"🌐 Raport HTML zapisany: {html_file}")
        
        print("="*80)
        
        # Podsumowanie końcowe
        if summary['failed_suites'] == 0:
            print("🎉 WSZYSTKIE TESTY ZAKOŃCZONE POMYŚLNIE!")
        else:
            print("⚠️ NIEKTÓRE TESTY ZAKOŃCZYŁY SIĘ NIEPOWODZENIEM")
            
        return {
            'json_report': report_file,
            'html_report': html_file
        }
        
    def _generate_html_report(self) -> str:
        """Generuj raport HTML"""
        summary = self.results['summary']
        
        html = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FaktuLove E2E Test Report</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 12px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 40px; 
            text-align: center;
        }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        
        .summary {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            padding: 30px; 
            background: #f8f9fa;
        }}
        .metric {{ 
            background: white; 
            padding: 25px; 
            border-radius: 10px; 
            text-align: center; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-left: 5px solid #007bff;
        }}
        .metric.success {{ border-left-color: #28a745; }}
        .metric.danger {{ border-left-color: #dc3545; }}
        .metric h3 {{ margin: 0; font-size: 2.2em; color: #333; }}
        .metric p {{ margin: 10px 0 0 0; color: #666; font-weight: 500; }}
        
        .content {{ padding: 30px; }}
        .section {{ margin: 30px 0; }}
        .section h2 {{ 
            color: #333; 
            border-bottom: 3px solid #eee; 
            padding-bottom: 15px; 
            margin-bottom: 25px;
        }}
        
        .test-suite {{ 
            margin: 20px 0; 
            padding: 20px; 
            border-radius: 10px; 
            border-left: 5px solid;
            background: #f8f9fa;
        }}
        .test-suite.success {{ 
            border-left-color: #28a745; 
            background: #d4edda;
        }}
        .test-suite.failure {{ 
            border-left-color: #dc3545; 
            background: #f8d7da;
        }}
        
        .suite-header {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 10px;
        }}
        .suite-name {{ font-weight: bold; font-size: 1.2em; }}
        .suite-duration {{ color: #666; }}
        .suite-error {{ 
            margin-top: 10px; 
            padding: 10px; 
            background: rgba(220, 53, 69, 0.1); 
            border-radius: 5px; 
            font-family: monospace;
            font-size: 0.9em;
        }}
        
        .footer {{ 
            background: #343a40; 
            color: white; 
            padding: 20px; 
            text-align: center;
        }}
        
        @media (max-width: 768px) {{
            .summary {{ grid-template-columns: 1fr; }}
            .suite-header {{ flex-direction: column; align-items: flex-start; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 FaktuLove E2E Test Report</h1>
            <p><strong>URL:</strong> {self.results['base_url']}</p>
            <p><strong>Wygenerowano:</strong> {self.results['timestamp']}</p>
        </div>
        
        <div class="summary">
            <div class="metric">
                <h3>{summary['total_suites']}</h3>
                <p>Zestawy Testów</p>
            </div>
            <div class="metric success">
                <h3>{summary['passed_suites']}</h3>
                <p>Pomyślne</p>
            </div>
            <div class="metric danger">
                <h3>{summary['failed_suites']}</h3>
                <p>Niepowodzenia</p>
            </div>
            <div class="metric">
                <h3>{summary['total_tests']}</h3>
                <p>Łączne Testy</p>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📋 Wyniki Zestawów Testów</h2>
"""
        
        for suite_name, result in self.results['test_suites'].items():
            status_class = 'success' if result['success'] else 'failure'
            status_icon = '✅' if result['success'] else '❌'
            duration = result.get('duration', 0)
            
            html += f"""
                <div class="test-suite {status_class}">
                    <div class="suite-header">
                        <div class="suite-name">{status_icon} {suite_name}</div>
                        <div class="suite-duration">{duration:.1f}s</div>
                    </div>
"""
            
            if 'tests' in result:
                tests = result['tests']
                html += f"""
                    <div>Testy: {tests.get('total', 0)} | Pomyślne: {tests.get('passed', 0)} | Niepowodzenia: {tests.get('failed', 0)}</div>
"""
            
            if not result['success'] and 'error' in result:
                html += f"""
                    <div class="suite-error">
                        <strong>Błąd:</strong> {result['error']}
                    </div>
"""
            
            html += """
                </div>
"""
        
        html += f"""
            </div>
        </div>
        
        <div class="footer">
            <p>Raport wygenerowany przez FaktuLove E2E Test Orchestrator</p>
            <p>© 2025 FaktuLove - System zarządzania fakturami z OCR</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html


def main():
    """Główna funkcja"""
    parser = argparse.ArgumentParser(description='FaktuLove E2E Test Orchestrator')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='URL aplikacji do testowania')
    parser.add_argument('--install-deps', action='store_true',
                       help='Zainstaluj wymagane zależności')
    
    args = parser.parse_args()
    
    if args.install_deps:
        print("📦 Instalowanie zależności testowych...")
        
        # Instaluj Python dependencies
        subprocess.run([sys.executable, '-m', 'pip', 'install', 
                       'selenium', 'playwright', 'requests', 'pytest'])
        
        # Instaluj Playwright browsers
        subprocess.run([sys.executable, '-m', 'playwright', 'install'])
        
        print("✅ Zależności zainstalowane")
        return
    
    # Uruchom testy
    orchestrator = E2ETestOrchestrator(args.url)
    success = orchestrator.run_all_tests()
    
    # Zwróć odpowiedni kod wyjścia
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()