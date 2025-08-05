# Flask Backend with CleanCloud Integration

This Flask backend now integrates with CleanCloud to automatically purchase and send gift cards when redemption codes are successfully redeemed.

## How It Works

1. **User redeems a code** through the frontend
2. **Code is validated and marked as redeemed** in Supabase database
3. **CleanCloud gift card is automatically purchased** using configured accounts
4. **Gift card is sent via email** to the user who redeemed the code

## Configuration

### Environment Variables (.env file):
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
CLEANCLOUD_API_TOKEN=your_cleancloud_api_token
GIFT_CARD_AMOUNT=10.0
```

### Gift Card Source Accounts:
Edit `gift_card_source_accounts.txt` and add CleanCloud customer IDs (one per line):
```
414
512
678
```

These accounts will be charged for gift card purchases. The system tries each account until one succeeds.

## Dependencies

Make sure to install required packages:
```bash
pip install flask flask-cors python-dotenv requests supabase
```

## Running the Backend

```bash
cd flask_backend
python app.py
```

Server runs on http://localhost:5000

## API Response

### Successful redemption with gift card:
```json
{
  "success": true,
  "message": "Code redeemed successfully! A $10.0 gift card has been sent to your email."
}
```

### Successful redemption but gift card failed:
```json
{
  "success": true,
  "message": "Code redeemed successfully! However, there was an issue sending your gift card. Please contact support."
}
```

## Logs

The system provides detailed logging for:
- Code redemption process
- CleanCloud API calls
- Gift card purchase attempts
- Error handling

Check the console output when running the Flask app for detailed logs.

## Testing

1. Start the Flask backend
2. Use the frontend to redeem a valid code
3. Check console logs for the complete flow
4. Verify gift card was sent via CleanCloud admin panel
