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
    this.codeInput.addEventListener("input", () => {
      this.filterCodeInput();
      this.checkFields();
    });
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

  filterCodeInput() {
    const currentValue = this.codeInput.value;

    // // Remove any non-alphanumeric characters and convert to uppercase
    // const filteredValue = currentValue.replace(/[^A-Za-z0-9]/g, '').toUpperCase();

    // Remove only dash characters and convert to uppercase
    const filteredValue = currentValue.replace(/-/g, '').toUpperCase();
    
    // Only update if the value changed to prevent cursor jumping
    if (currentValue !== filteredValue) {
      this.codeInput.value = filteredValue;
    }
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
    
    // Only show validation warnings if we're not showing a success/error message
    if (this.resultEl.textContent.includes("✅") || this.resultEl.textContent.includes("❌")) {
      // Don't clear success/error messages
      return;
    }
    
    // Show validation warnings - prioritize email mismatch, then phone mismatch
    if (confirmEmail && email && !emailsMatch) {
      this.displayResult("⚠️ Emails do not match", "orange");
    } else if (confirmPhone && phone && !phonesMatch) {
      this.displayResult("⚠️ Phone numbers do not match", "orange");
    } else {
      // Clear any previous validation messages when everything is OK
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
    console.log("displayResult called with:", message, color);
    this.resultEl.textContent = message;
    this.resultEl.style.color = color;
    console.log("Result element updated:", this.resultEl.textContent);
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
        recipient_email: email,
        recipient_phone: phone,
        metadata: { 
          source: "webpage"
        }
      };

      // Use local backend if running locally, otherwise use production
      const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:'
        ? 'http://localhost:5000/redeem'
        : window.location.origin + '/redeem/redeem_api.php';  // Direct PHP file in redeem subdirectory

      console.log("Using API URL:", API_URL);

      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(requestData)
      });

      console.log("Response status:", response.status);
      console.log("Response ok:", response.ok);
      
      const result = await response.json();
      console.log("Response data:", result);

      if (response.ok && result.success) {
        this.displayResult("✅ " + result.message, "green");
        // Clear the code field on successful redemption
        this.codeInput.value = "";
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
