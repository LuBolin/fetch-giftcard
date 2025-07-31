# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack gift card management system with a Flask backend, Supabase database, and vanilla JavaScript frontend for secure code redemption.

## Architecture

### Backend (`/backend/`)
- **app.py**: Flask server with CORS, serves frontend and provides `/redeem` API endpoint
- **supabase_tool.py**: Database client wrapper with comprehensive gift code management methods
- **generate_codes.py**: Creates unique 16-character alphanumeric codes with CSV output
- **upload_codes.py**: Bulk upload and distribution management
- **worker.py**: Background operations and utilities

### Frontend (`/frontend/`)
- **redeem.html**: Redemption interface with dual-entry confirmation
- **redeem.js**: Client-side validation, API communication, security measures
- **redeem.css**: Responsive styling

### Database Schema (Supabase)
Table: `unique_codes`
- `id` (UUID, primary key)
- `unique_code` (varchar, unique, indexed)
- `amount` (numeric)
- `created_at` (timestamp)
- `is_redeemed` (boolean)
- `redeemed_at` (timestamp)
- `used_email` (varchar)
- `expiry_date` (date)
- `created_by` (varchar)
- `batch_id` (varchar)
- `notes` (text)

## Development Commands

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py  # Runs on http://localhost:5002
```

### Environment Variables
Create `.env` file in `/backend/`:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Frontend Development
The frontend automatically switches between local (http://localhost:5002) and production APIs based on the hostname.

## Key Features & Security

1. **Code Redemption Security**:
   - Dual-entry confirmation required
   - Copy/paste disabled on code input fields
   - Input filtering (alphanumeric only, auto-uppercase)
   - Rate limiting considerations

2. **API Endpoints**:
   - `POST /redeem`: Redeems gift code
     - Body: `{code, email, confirmCode}`
     - Returns: `{success, message, amount?}`

3. **Database Operations** (via supabase_tool.py):
   - `check_code_validity()`: Validates code existence and redemption status
   - `redeem_code()`: Atomic redemption with email recording
   - `bulk_insert_codes()`: Batch insertion with duplicate prevention
   - `get_redeemed_codes()`: Analytics and reporting

## Code Generation & Management

Generate new codes:
```bash
python backend/generate_codes.py
# Creates 'unique_codes_YYYYMMDD_HHMMSS.csv'
```

Upload codes to database:
```bash
python backend/upload_codes.py
```

## Testing Considerations

- Test code redemption flow end-to-end
- Verify duplicate code prevention
- Check expiry date validation
- Test frontend validation rules
- Ensure API error handling works correctly

## Deployment

The application is configured for deployment on Render.com:
- Backend serves both API and static frontend files
- Production URL configured in frontend JavaScript
- CORS enabled for cross-origin requests