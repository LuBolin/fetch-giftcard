class GiftCodeRedeemer {
  constructor() {
    this.codeInput = document.getElementById("code");
    this.emailInput = document.getElementById("email");
    this.confirmEmailInput = document.getElementById("confirmEmail");
    this.phoneInput = document.getElementById("phone");
    this.confirmPhoneInput = document.getElementById("confirmPhone");
    this.redeemBtn = document.getElementById("redeemBtn");
    this.resultEl = document.getElementById("result");

    // Initially disable confirmation fields
    this.confirmEmailInput.disabled = true;
    this.confirmPhoneInput.disabled = true;

    this.setupEventListeners();
    this.preventCopyPaste();
  }

  setupEventListeners() {
    this.codeInput.addEventListener("input", () => this.checkFields());
    this.emailInput.addEventListener("input", () => this.handleEmailInput());
    this.confirmEmailInput.addEventListener("input", () => this.checkFields());
    this.phoneInput.addEventListener("input", () => this.handlePhoneInput());
    this.confirmPhoneInput.addEventListener("input", () => this.checkFields());
    this.redeemBtn.addEventListener("click", () => this.redeemCode());
  }

  handleEmailInput() {
    const email = this.emailInput.value.trim();
    
    // Enable/disable confirm email field based on email input
    if (email) {
      this.confirmEmailInput.disabled = false;
    } else {
      this.confirmEmailInput.disabled = true;
      this.confirmEmailInput.value = "";
    }
    
    this.checkFields();
  }

  handlePhoneInput() {
    const phone = this.phoneInput.value.trim();
    
    // Enable/disable confirm phone field based on phone input
    if (phone) {
      this.confirmPhoneInput.disabled = false;
    } else {
      this.confirmPhoneInput.disabled = true;
      this.confirmPhoneInput.value = "";
    }
    
    this.checkFields();
  }

  preventCopyPaste() {
    const fields = [this.emailInput, this.confirmEmailInput, this.phoneInput, this.confirmPhoneInput];
    
    fields.forEach(field => {
      // Prevent copy (Ctrl+C)
      field.addEventListener('copy', (e) => {
        e.preventDefault();
        return false;
      });
      
      // Prevent paste (Ctrl+V)
      field.addEventListener('paste', (e) => {
        e.preventDefault();
        return false;
      });
      
      // Prevent cut (Ctrl+X)
      field.addEventListener('cut', (e) => {
        e.preventDefault();
        return false;
      });
      
      // Prevent right-click context menu
      field.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
      });
      
      // Prevent drag and drop
      field.addEventListener('drop', (e) => {
        e.preventDefault();
        return false;
      });
    });
  }

  checkFields() {
    const code = this.codeInput.value.trim();
    const email = this.emailInput.value.trim();
    const confirmEmail = this.confirmEmailInput.value.trim();
    const phone = this.phoneInput.value.trim();
    const confirmPhone = this.confirmPhoneInput.value.trim();
    
    // Check matching conditions
    const emailsMatch = !confirmEmail || !email || email === confirmEmail;
    const phonesMatch = !confirmPhone || !phone || phone === confirmPhone;
    
    // All fields must be filled and emails/phones must match
    const allFieldsFilled = code && email && confirmEmail && phone && confirmPhone;
    
    this.redeemBtn.disabled = !allFieldsFilled || !emailsMatch || !phonesMatch;
    
    // Show validation warnings - prioritize email mismatch, then phone mismatch
    if (confirmEmail && email && !emailsMatch) {
      this.displayResult("⚠️ Emails do not match", "orange");
    } else if (confirmPhone && phone && !phonesMatch) {
      this.displayResult("⚠️ Phone numbers do not match", "orange");
    } else {
      // Clear any previous error messages when everything is OK
      this.resultEl.textContent = "";
    }
  }

  setLoadingState(isLoading) {
    this.codeInput.disabled = isLoading;
    this.emailInput.disabled = isLoading;
    this.confirmEmailInput.disabled = isLoading;
    this.phoneInput.disabled = isLoading;
    this.confirmPhoneInput.disabled = isLoading;
    this.redeemBtn.disabled = isLoading;
    this.redeemBtn.textContent = isLoading ? "Redeeming..." : "Redeem";
  }

  displayResult(message, color) {
    this.resultEl.textContent = message;
    this.resultEl.style.color = color;
  }

  async redeemCode() {
    const code = this.codeInput.value.trim();
    const email = this.emailInput.value.trim();
    const confirmEmail = this.confirmEmailInput.value.trim();
    const phone = this.phoneInput.value.trim();
    const confirmPhone = this.confirmPhoneInput.value.trim();

    // Clear previous response
    this.resultEl.textContent = "";
    this.resultEl.style.color = "";

    // Validation
    if (!code || !email || !confirmEmail || !phone || !confirmPhone) {
      this.displayResult("⚠️ Please fill in all fields.", "orange");
      return;
    }

    if (email !== confirmEmail) {
      this.displayResult("⚠️ Emails do not match.", "orange");
      return;
    }

    if (phone !== confirmPhone) {
      this.displayResult("⚠️ Phone numbers do not match.", "orange");
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      this.displayResult("⚠️ Please enter a valid email address.", "orange");
      return;
    }

    this.setLoadingState(true);

    try {
      const requestData = {
        code: code,
        recipient: email,
        metadata: { 
          source: "webpage",
          phone: phone,
          email_confirmed: true,
          phone_confirmed: true
        }
      };

      const response = await fetch("https://fetch-giftcard.onrender.com/redeem", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(requestData)
      });

      const result = await response.json();

      if (response.ok && result.success) {
        this.displayResult("✅ " + result.message, "green");
      } else {
        this.displayResult("❌ " + result.message, "red");
      }

    } catch (err) {
      this.displayResult("❌ Network or server error.", "red");
      console.error(err);
    } finally {
      this.setLoadingState(false);
      this.checkFields(); // Re-check if button should be enabled
    }
  }
}

// Initialize the redeemer when the DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new GiftCodeRedeemer();
});
