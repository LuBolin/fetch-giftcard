class GiftCodeRedeemer {
  constructor() {
    this.codeInput = document.getElementById("code");
    this.usernameInput = document.getElementById("username");
    this.redeemBtn = document.getElementById("redeemBtn");
    this.resultEl = document.getElementById("result");

    this.setupEventListeners();
  }

  setupEventListeners() {
    this.codeInput.addEventListener("input", () => this.checkFields());
    this.usernameInput.addEventListener("input", () => this.checkFields());
    this.redeemBtn.addEventListener("click", () => this.redeemCode());
  }

  checkFields() {
    const code = this.codeInput.value.trim();
    const username = this.usernameInput.value.trim();
    
    this.redeemBtn.disabled = !code || !username;
  }

  setLoadingState(isLoading) {
    this.codeInput.disabled = isLoading;
    this.usernameInput.disabled = isLoading;
    this.redeemBtn.disabled = isLoading;
    this.redeemBtn.textContent = isLoading ? "Redeeming..." : "Redeem";
  }

  displayResult(message, color) {
    this.resultEl.textContent = message;
    this.resultEl.style.color = color;
  }

  async redeemCode() {
    const code = this.codeInput.value.trim();
    const username = this.usernameInput.value.trim();

    // Clear previous response
    this.resultEl.textContent = "";
    this.resultEl.style.color = "";

    if (!code || !username) {
      this.displayResult("⚠️ Please enter both code and username.", "orange");
      return;
    }

    this.setLoadingState(true);

    try {
      const requestData = {
        code: code,
        recipient: username,
        metadata: { source: "webpage" }
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
