document.addEventListener('DOMContentLoaded', function() {
    // Toggle email form modal visibility
    function toggleEmailPopup(show) {
        const modal = document.getElementById('emailTemplateFormPopup');
        if (show) {
            modal.style.display = 'flex';  // Show the modal
        } else {
            modal.style.display = 'none';  // Hide the modal
        }
    }

    // Show the email form when the "New Template" button is clicked
    document.getElementById('new-template-btn').addEventListener('click', function() {
        document.getElementById('emailTemplateForm').reset();  // Reset the form
        toggleEmailPopup(true);  // Show the modal
    });

    // Close the modal when the "x" button is clicked
    document.querySelector('.close').addEventListener('click', function() {
        toggleEmailPopup(false);  // Close the modal
    });

    // Close the modal when clicking outside of the modal content
    window.onclick = function(event) {
        const modal = document.getElementById('emailTemplateFormPopup');
        if (event.target === modal) {
            toggleEmailPopup(false);
        }
    };

    // Submit the email template form
    function submitEmailTemplateForm() {
        const formData = new FormData(document.getElementById('emailTemplateForm'));

        // Send form data to the backend via Fetch
        fetch('/api/templates', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Form submission failed.');
            }
        })
        .then(data => {
            console.log('Success:', data);
            addTemplateEntryToDOM(data);  // Update DOM with the new template entry
            toggleEmailPopup(false);  // Close the modal after successful submission
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was an error submitting the form. Please try again.');
        });
    }

    // Add the new email template entry to the DOM dynamically
    function addTemplateEntryToDOM(templateData) {
        const newEntryDiv = document.createElement('div');
        newEntryDiv.className = 'template-entry';
        newEntryDiv.innerHTML = `
            <p><strong>Subject:</strong> ${templateData.subject}</p>
            <p><strong>Body:</strong> ${templateData.body}</p>
        `;
        document.getElementById('template-entries').appendChild(newEntryDiv);
    }

    // Attach the form submit action to the "Submit" button
    document.querySelector('#emailTemplateForm button[type="button"]').addEventListener('click', submitEmailTemplateForm);
});
