# cPanel Deployment Instructions

## Prerequisites
- cPanel hosting account with PHP 7.4+ support
- Access to cPanel File Manager or FTP
- SSL certificate installed (for HTTPS)

## Deployment Steps

### 1. Prepare Files
1. Create a `.env` file in the `php_backend` directory with your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

### 2. Upload Files

#### Option A: Single Domain Setup (e.g., yourdomain.com)
Upload the following structure to your `public_html` directory:
```
public_html/
├── index.php (from php_backend/index.php)
├── redeem.php (from php_backend/redeem.php)
├── redeem_api.php (from php_backend/redeem_api.php) 
├── config.php (from php_backend/config.php)
├── SupabaseClient.php (from php_backend/SupabaseClient.php)
├── .htaccess (from php_backend/.htaccess)
├── .env (your environment file)
├── test.php (from php_backend/test.php - remove after testing)
├── redeem.html (from frontend/redeem.html)
├── redeem.css (from frontend/redeem.css)
└── redeem.js (from frontend/redeem.js)
```

#### Option B: Subdirectory Setup (e.g., yourdomain.com/giftcard)
1. Create a subdirectory in `public_html` (e.g., `giftcard`)
2. Upload all files to that subdirectory
3. Update the .htaccess RewriteBase:
   ```apache
   RewriteBase /giftcard/
   ```

### 3. Set File Permissions
Using cPanel File Manager or FTP:
- All PHP files: 644
- .htaccess: 644
- .env: 600 (more restrictive for security)
- Directories: 755

### 4. Configure Error Logging
Create an `error_log` file in your installation directory with 644 permissions to capture PHP errors.

### 5. Test the Installation
1. Visit your domain (e.g., `https://yourdomain.com` or `https://yourdomain.com/giftcard`)
2. You should see the gift card redemption page
3. Check browser console for any errors

## Security Considerations

1. **Protect .env file** - Add to .htaccess:
   ```apache
   # Protect .env file
   <Files .env>
       Order allow,deny
       Deny from all
   </Files>
   ```

2. **Disable directory listing** - Already included in .htaccess

3. **Use HTTPS** - Ensure your cPanel has SSL certificate installed

## Troubleshooting

### Common Issues:

1. **500 Internal Server Error**
   - Check .htaccess syntax
   - Verify PHP version (needs 7.4+)
   - Check error_log file

2. **404 Not Found on /redeem**
   - Ensure mod_rewrite is enabled
   - Check .htaccess is being processed

3. **CORS Issues**
   - The PHP backend already has CORS headers configured
   - If issues persist, check if cPanel is adding conflicting headers

4. **Database Connection Failed**
   - Verify .env file exists and has correct credentials
   - Check file permissions on .env (should be readable by PHP)

### Testing Commands (via cPanel Terminal or SSH):
```bash
# Test if PHP can read .env
php -r "print_r(parse_ini_file('.env'));"

# Test Supabase connection
php -r "require 'config.php'; echo SUPABASE_URL;"
```

## Updating the Application
1. Upload new files via FTP/File Manager
2. Clear browser cache
3. Test functionality

## Support
Check error_log file in your installation directory for detailed error messages.