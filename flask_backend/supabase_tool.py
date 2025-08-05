from datetime import datetime, timezone
import supabase

# columns: code, serial_number, uploaded_at, expiry_date, distributed_to, distributed_at
# is_redeemed, redeemed_at, recipient_email, recipient_phone, metadata, card_value

# uploaded_at, redeemed_at and distributed_at are TIMESTAMPTZ
# expiry_date is a DATE

class SupabaseClient(supabase.Client):

    def __init__(self, url, key):
        super().__init__(url, key)

    def upload_codes(self, codes, metadata = None, card_value = None):
        # Prepare all data for bulk insert
        bulk_data = []
        for code in codes:
            data = {
                "code": code,
                "metadata": metadata,
            }
            if card_value is not None:
                data["card_value"] = card_value
            bulk_data.append(data)

        try:
            response = self.table("gift_codes").insert(bulk_data).execute()
            print(f"✅ Successfully inserted {len(codes)} codes in bulk")
            return response.data
        except Exception as e:
            error_message = e.message if hasattr(e, 'message') else str(e)
            print(f"❌ Error bulk inserting codes: {error_message}")
            raise e

    def redeem_code(self, code, recipient_email, recipient_phone, metadata=None):
        check_res = self.table("gift_codes").select("*").eq("code", code).execute()
        rows = check_res.data

        if not rows:
            raise ValueError(f"Code '{code}' not found in database.")

        row = rows[0]
        if row.get("is_redeemed"):
            redeemed_at = row.get("redeemed_at")
            if redeemed_at:
                # Parse the timestamp and format it nicely
                try:
                    if isinstance(redeemed_at, str):
                        # Handle ISO format with or without 'Z'
                        redeemed_datetime = datetime.fromisoformat(redeemed_at.replace('Z', '+00:00'))
                    else:
                        redeemed_datetime = redeemed_at
                    
                    # Format as a readable date and time
                    formatted_time = redeemed_datetime.strftime("%B %d, %Y at %I:%M %p UTC")
                    raise ValueError(f"Code '{code}' has already been redeemed on {formatted_time}.")
                except (ValueError, TypeError):
                    # Fallback if timestamp parsing fails
                    raise ValueError(f"Code '{code}' has already been redeemed on {redeemed_at}.")
            else:
                # Fallback if no timestamp is available
                raise ValueError(f"Code '{code}' has already been redeemed.")
        
        expiry_date = row.get("expiry_date")
        if expiry_date:
            # expiry_date is a DATE field, so we compare with today's date
            from datetime import date
            if isinstance(expiry_date, str):
                expiry_date_obj = datetime.fromisoformat(expiry_date.replace('Z', '')).date()
            else:
                expiry_date_obj = expiry_date
            
            if date.today() > expiry_date_obj:
                raise ValueError(f"Code '{code}' has expired on {expiry_date_obj}.")

        data = {
            "is_redeemed": True,
            "redeemed_at": datetime.now(timezone.utc).isoformat(),
            "recipient_email": recipient_email,
            "recipient_phone": recipient_phone,
            "metadata": metadata
        }
        
        try:
            response = self.table("gift_codes").update(data)\
                .eq("code", code).eq("is_redeemed", False).execute()
            # response: postgrest.base_request_builder.APIResponse[TypeVar]
            # response.data: list of dicts
            # response.data[0]: dict with the updated row
            data = response.data
            if not data:
                raise ValueError(f"Code {code} not found or already redeemed.")
            updated_row = data[0]
            print(f"✅ Redeemed {code} for email {recipient_email}")
            print(f"Updated row: {updated_row}")
        except Exception as e:
            raise e
    
    # For testing only
    def reset_code(self, code):
        try:
            response = self.table("gift_codes").update({
                "is_redeemed": False,
                "recipient_email": None,
                "recipient_phone": None,
                "redeemed_at": None
            }).eq("code", code).execute()
            if response.data:
                print(f"✅ Reset {code} successfully.")
            else:
                print(f"❌ Code {code} not found or not redeemed.")
        except Exception as e:
            error_message = e.message if hasattr(e, 'message') else str(e)
            print(f"❌ Error resetting {code}: {error_message}")

    def update_expiry(self, start_serial, end_serial, new_expiry_date: datetime):
        # update all codes in the range [start_serial, end_serial] that are not redeemed
        try:
            # Ensure new_expiry_date is a date object for DATE field
            if isinstance(new_expiry_date, datetime):
                expiry_value = new_expiry_date.date().isoformat()
            else:
                expiry_value = new_expiry_date.isoformat()
                
            response = self.table("gift_codes").update({
                "expiry_date": expiry_value
            }).gte("serial_number", start_serial).lte("serial_number", end_serial).eq("is_redeemed", False).execute()

            if response.data:
                print(f"✅ Updated expiry date for codes from {start_serial} to {end_serial}.")
            else:
                print(f"❌ No codes found in the range {start_serial} to {end_serial} that are not redeemed.")
        except Exception as e:
            error_message = e.message if hasattr(e, 'message') else str(e)
            print(f"❌ Error updating expiry date: {error_message}")
    
    def distribute_cards(self, start_serial, end_serial, distributed_to, distributed_at=None):
        if distributed_at is None:
            distributed_at = datetime.now(timezone.utc).isoformat()
        try:
            response = self.table("gift_codes").update({
                "distributed_to": distributed_to,
                "distributed_at": distributed_at
            }).gte("serial_number", start_serial).lte("serial_number", end_serial).eq("is_redeemed", False).execute()

            if response.data:
                print(f"✅ Distributed codes from {start_serial} to {end_serial} to {distributed_to}.")
            else:
                print(f"❌ No codes found in the range {start_serial} to {end_serial} that are not redeemed.")
        except Exception as e:
            error_message = e.message if hasattr(e, 'message') else str(e)
            print(f"❌ Error distributing cards: {error_message}")
