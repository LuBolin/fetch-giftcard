# PHP Backend for Fetch Gift Card System

This is a PHP implementation of the gift card redemption backend, designed to be deployed on shared hosting platforms like HostGator.

## Requirements

- PHP 7.4 or higher
- cURL extension
- JSON extension
- Apache with mod_rewrite enabled

## Installation

1. Upload all files to your web hosting directory

2. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

4. Ensure proper file permissions:
   ```bash
   chmod 644 .env
   chmod 755 .
   ```

## File Structure

- `index.php` - Main entry point, routes requests and serves frontend
- `redeem.php` - API endpoint for code redemption
- `SupabaseTool.php` - Database client for Supabase operations
- `config.php` - Configuration loader
- `generate_codes.php` - CLI script for generating gift codes
- `upload_codes.php` - CLI script for uploading codes to database
- `.htaccess` - Apache configuration for routing and CORS

## API Endpoints

### POST /redeem
Redeems a gift card code.

Request body:
```json
{
  "code": "ABCD1234EFGH5678",
  "email": "user@example.com",
  "confirmCode": "ABCD1234EFGH5678"
}
```

Response:
```json
{
  "success": true,
  "message": "Code redeemed successfully!",
  "amount": 100
}
```

## CLI Scripts

### Generate Codes
```bash
php generate_codes.php [count] [amount]
# Example: php generate_codes.php 100 50.00
```

### Upload Codes to Database
```bash
php upload_codes.php <csv_file> [expiry_date] [batch_id]
# Example: php upload_codes.php codes.csv 2024-12-31
```

## Deployment on HostGator

1. Upload all files via FTP or File Manager
2. Place files in `public_html` or subdirectory
3. Ensure `.htaccess` is properly uploaded
4. Configure `.env` with your credentials
5. Test the redemption endpoint

## Security Notes

- The `.env` file should not be accessible via web
- Error logs are written to `error.log`
- CORS is configured for all origins (adjust in production)
- All database operations use prepared statements