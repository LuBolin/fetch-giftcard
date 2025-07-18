class GiftCodeRedeemer {
  constructor() {
    this.codeInput = document.getElementById("code");
    this.emailInput = document.getElementById("email");
    this.confirmEmailInput = document.getElementById("confirmEmail");
    this.phoneInput = document.getElementById("phone");
    this.confirmPhoneInput = document.getElementById("confirmPhone");
    this.redeemBtn = document.getElementById("redeemBtn");
    this.resultEl = document.getElementById("result");

    this.setupEventListeners();
  }

  setupEventListeners() {
    this.codeInput.addEventListener("input", () => this.checkFields());
    this.emailInput.addEventListener("input", () => this.checkFields());
    this.confirmEmailInput.addEventListener("input", () => this.checkFields());
    this.phoneInput.addEventListener("input", () => this.checkFields());
    this.confirmPhoneInput.addEventListener("input", () => this.checkFields());
    this.redeemBtn.addEventListener("click", () => this.redeemCode());
  }

  checkFields() {
    const code = this.codeInput.value.trim();
    const email = this.emailInput.value.trim();
    const confirmEmail = this.confirmEmailInput.value.trim();
    const phone = this.phoneInput.value.trim();
    const confirmPhone = this.confirmPhoneInput.value.trim();
    
    // All fields must be filled and emails/phones must match
    const allFieldsFilled = code && email && confirmEmail && phone && confirmPhone;
    const emailsMatch = email === confirmEmail;
    const phonesMatch = phone === confirmPhone;
    
    this.redeemBtn.disabled = !allFieldsFilled || !emailsMatch || !phonesMatch;
    
    // Show validation warnings
    if (confirmEmail && !emailsMatch) {
      this.displayResult("⚠️ Emails do not match", "orange");
    } else if (confirmPhone && !phonesMatch) {
      this.displayResult("⚠️ Phone numbers do not match", "orange");
    } else if (confirmEmail && confirmPhone && emailsMatch && phonesMatch && allFieldsFilled) {
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
