#!/usr/bin/env python3
"""
Web Security Auditor - Defensive Security Analysis
Checks for common security vulnerabilities without exploitation
"""

import requests
import re
from urllib.parse import urlparse, urljoin

def check_security_headers(url):
    """Check for important security headers"""
    print("\n" + "="*60)
    print("🔒 SECURITY HEADERS ANALYSIS")
    print("="*60)

    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        headers = response.headers

        security_headers = {
            'Strict-Transport-Security': 'HSTS - Forces HTTPS',
            'X-Frame-Options': 'Prevents clickjacking',
            'X-Content-Type-Options': 'Prevents MIME sniffing',
            'Content-Security-Policy': 'Prevents XSS attacks',
            'X-XSS-Protection': 'XSS filter (legacy)',
            'Referrer-Policy': 'Controls referrer information',
            'Permissions-Policy': 'Controls browser features',
        }

        missing = []
        present = []

        for header, description in security_headers.items():
            if header in headers:
                present.append(f"✓ {header}: {headers[header][:50]}...")
            else:
                missing.append(f"✗ {header} - {description}")

        if present:
            print("\n✅ Present Headers:")
            for h in present:
                print(f"  {h}")

        if missing:
            print("\n⚠️  Missing Headers:")
            for h in missing:
                print(f"  {h}")

        # Check cookies
        if 'Set-Cookie' in headers:
            cookie = headers['Set-Cookie']
            print(f"\n🍪 Cookie Settings:")
            print(f"  {cookie[:100]}...")
            if 'Secure' not in cookie:
                print("  ⚠️  Missing 'Secure' flag")
            if 'HttpOnly' not in cookie:
                print("  ⚠️  Missing 'HttpOnly' flag")
            if 'SameSite' not in cookie:
                print("  ⚠️  Missing 'SameSite' attribute")

        return response

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_common_files(base_url):
    """Check for exposed sensitive files"""
    print("\n" + "="*60)
    print("📁 EXPOSED FILES CHECK")
    print("="*60)

    common_files = [
        '.git/config',
        '.env',
        '.env.local',
        '.env.production',
        'config.php',
        'wp-config.php',
        '.htaccess',
        'phpinfo.php',
        'admin',
        'administrator',
        'wp-admin',
        'phpmyadmin',
        'backup.zip',
        'backup.sql',
        'database.sql',
        'robots.txt',
        'sitemap.xml',
        '.DS_Store',
        'package.json',
        'composer.json',
        '.git/HEAD',
    ]

    exposed = []
    safe = 0

    for file in common_files:
        url = urljoin(base_url, file)
        try:
            response = requests.get(url, timeout=5, allow_redirects=False)
            if response.status_code == 200:
                exposed.append(f"⚠️  EXPOSED: {file} (Status: {response.status_code})")
            else:
                safe += 1
        except:
            safe += 1

    if exposed:
        print("\n⚠️  Potentially Exposed Files:")
        for item in exposed:
            print(f"  {item}")
    else:
        print("\n✅ No common sensitive files exposed")

    print(f"\n📊 Summary: {safe}/{len(common_files)} files properly protected")

def analyze_html_content(response):
    """Analyze HTML for security issues"""
    print("\n" + "="*60)
    print("🔍 HTML CONTENT ANALYSIS")
    print("="*60)

    if not response:
        return

    html = response.text

    # Check for comments with sensitive info
    comments = re.findall(r'<!--(.*?)-->', html, re.DOTALL)
    if comments:
        print(f"\n💬 Found {len(comments)} HTML comments:")
        for i, comment in enumerate(comments[:5], 1):
            cleaned = comment.strip()[:100]
            if any(keyword in cleaned.lower() for keyword in ['password', 'key', 'secret', 'token', 'api']):
                print(f"  ⚠️  Comment {i} contains sensitive keywords: {cleaned}")
            else:
                print(f"  ℹ️  Comment {i}: {cleaned}")

    # Check for inline scripts
    inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    print(f"\n📜 Inline Scripts: {len(inline_scripts)} found")
    if len(inline_scripts) > 10:
        print("  ⚠️  Many inline scripts - Consider using CSP")

    # Check for external scripts
    external_scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html)
    if external_scripts:
        print(f"\n🌐 External Scripts ({len(external_scripts)}):")
        for script in external_scripts[:10]:
            domain = urlparse(script).netloc
            print(f"  - {domain or 'relative path'}: {script[:60]}")

    # Check for forms
    forms = re.findall(r'<form[^>]*>(.*?)</form>', html, re.DOTALL | re.IGNORECASE)
    if forms:
        print(f"\n📋 Forms Found: {len(forms)}")
        for i, form in enumerate(forms, 1):
            if 'csrf' not in form.lower() and 'token' not in form.lower():
                print(f"  ⚠️  Form {i}: No CSRF token detected")
            if 'action=' in form.lower():
                action = re.search(r'action=["\']([^"\']+)["\']', form, re.IGNORECASE)
                if action:
                    print(f"  → Action: {action.group(1)}")

    # Check for email addresses
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', html)
    if emails:
        print(f"\n📧 Email Addresses Exposed: {len(set(emails))}")
        for email in list(set(emails))[:5]:
            print(f"  - {email}")

    # Check for API keys or tokens in HTML
    potential_keys = re.findall(r'(api[_-]?key|token|secret|password)["\']?\s*[:=]\s*["\']([^"\']{20,})["\']', html, re.IGNORECASE)
    if potential_keys:
        print(f"\n⚠️  CRITICAL: Potential API keys/secrets in HTML:")
        for key_type, key_value in potential_keys:
            print(f"  - {key_type}: {key_value[:20]}...")

def check_ssl_tls(url):
    """Check SSL/TLS configuration"""
    print("\n" + "="*60)
    print("🔐 SSL/TLS ANALYSIS")
    print("="*60)

    parsed = urlparse(url)

    if parsed.scheme == 'http':
        print("  ⚠️  WARNING: Site uses HTTP (not HTTPS)")
        print("  Recommendation: Enable HTTPS immediately")
    elif parsed.scheme == 'https':
        print("  ✅ Site uses HTTPS")
        try:
            response = requests.get(url, timeout=10)
            print(f"  ✅ SSL certificate valid")
        except requests.exceptions.SSLError as e:
            print(f"  ❌ SSL Error: {e}")

def check_information_disclosure(response):
    """Check for information disclosure"""
    print("\n" + "="*60)
    print("ℹ️  INFORMATION DISCLOSURE")
    print("="*60)

    if not response:
        return

    headers = response.headers

    # Check Server header
    if 'Server' in headers:
        print(f"  Server: {headers['Server']}")
        print("  ⚠️  Server version exposed - consider hiding")

    # Check X-Powered-By
    if 'X-Powered-By' in headers:
        print(f"  X-Powered-By: {headers['X-Powered-By']}")
        print("  ⚠️  Technology stack exposed - consider removing")

    # Check for version numbers in HTML
    html = response.text
    versions = re.findall(r'version["\']?\s*[:=]\s*["\']?([0-9]+\.[0-9]+\.[0-9]+)', html, re.IGNORECASE)
    if versions:
        print(f"  ⚠️  Version numbers found in HTML: {set(versions)}")

def generate_recommendations(url):
    """Generate security recommendations"""
    print("\n" + "="*60)
    print("💡 SECURITY RECOMMENDATIONS")
    print("="*60)

    recommendations = [
        "1. Enable all missing security headers (HSTS, CSP, X-Frame-Options)",
        "2. Implement Content Security Policy (CSP) to prevent XSS",
        "3. Add CSRF tokens to all forms",
        "4. Use HTTPS everywhere (enable HSTS)",
        "5. Set Secure, HttpOnly, and SameSite flags on cookies",
        "6. Remove or protect sensitive files (.git, .env, backups)",
        "7. Hide server version information",
        "8. Implement rate limiting on forms and API endpoints",
        "9. Add input validation and sanitization",
        "10. Regular security audits and penetration testing",
        "11. Keep all dependencies and frameworks updated",
        "12. Implement proper authentication and authorization",
        "13. Use secure password hashing (bcrypt, Argon2)",
        "14. Enable audit logging for security events",
        "15. Regular backup and disaster recovery plan",
    ]

    for rec in recommendations:
        print(f"  {rec}")

def main():
    url = input("Enter URL to audit (e.g., https://d.epicworld.tech/): ").strip()

    if not url.startswith('http'):
        url = 'https://' + url

    print(f"\n🔍 Starting Security Audit for: {url}")
    print(f"⏰ Time: {requests.utils.default_headers()}")

    # Run all checks
    check_ssl_tls(url)
    response = check_security_headers(url)
    check_common_files(url)
    analyze_html_content(response)
    check_information_disclosure(response)
    generate_recommendations(url)

    print("\n" + "="*60)
    print("✅ SECURITY AUDIT COMPLETE")
    print("="*60)
    print("\n⚠️  DISCLAIMER: This is a basic automated scan.")
    print("For comprehensive security, hire a professional penetration tester.")
    print("="*60)

if __name__ == "__main__":
    main()
