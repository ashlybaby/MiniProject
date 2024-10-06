// static/js/modal.js

// Get modal element
const modal = document.getElementById("budget-modal");

// Get open modal button
const openModalBtn = document.getElementById("open-budget-modal");

// Get close button
const closeBtn = document.querySelector(".close-button");

// Listen for open click
openModalBtn.addEventListener("click", () => {
    modal.style.display = "block";
});

// Listen for close click
closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
});

// Listen for outside click
window.addEventListener("click", (e) => {
    if (e.target == modal) {
        modal.style.display = "none";
    }
});

// Add Expense Functionality
document.addEventListener("DOMContentLoaded", () => {
    const addExpenseBtn = document.getElementById("add-expense");
    const expenseContainer = document.getElementById("expense-container");

    addExpenseBtn.addEventListener("click", () => {
        const newExpense = document.createElement("div");
        newExpense.classList.add("expense-item");
        newExpense.innerHTML = `
            <label for="category">Category:</label>
            <input type="text" name="expense-category" required>
            <label for="planned-expense">Planned Expense:</label>
            <input type="number" name="planned-expense" step="0.01" required>
            <label for="actual-expense">Actual Expense:</label>
            <input type="number" name="actual-expense" step="0.01" required>
            <button type="button" class="remove-expense">Remove</button>
        `;
        expenseContainer.appendChild(newExpense);
    });

    // Delegate event listener for remove buttons
    expenseContainer.addEventListener("click", (e) => {
        if (e.target && e.target.classList.contains("remove-expense")) {
            e.target.parentElement.remove();
        }
    });
});
