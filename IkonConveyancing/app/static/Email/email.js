document.addEventListener('DOMContentLoaded', function () {
    // Load templates when the page loads
    loadTemplates();

    // Event listener for the "New Template" button
    document.getElementById('new-template').addEventListener('click', function () {
        console.log('New Template button clicked'); // Debugging
        // Open the form for creating a new template
        document.getElementById('template-form-container').style.display = 'block';
        document.getElementById('template-form').reset();  // Clear any existing data in the form
    });

    // Event listener for the Cancel button
    document.getElementById('cancel-form').addEventListener('click', function () {
        console.log('Cancel button clicked'); // Debugging
        // Close the template form
        document.getElementById('template-form-container').style.display = 'none';
    });

    // Event listener for submitting the template form
    document.getElementById('template-form').addEventListener('submit', function (event) {
        event.preventDefault();
        console.log('Form submitted'); // Debugging
        saveTemplate(); // Save the template
    });
});

// Function to load templates (stub, replace with real API call)
function loadTemplates() {
    console.log('Templates loading...'); // Debugging
    // In reality, this would fetch the templates from the backend API
}

// Function to save a template (stub, replace with real API call)
function saveTemplate() {
    console.log('Saving template...'); // Debugging
    // In reality, this would save the template to the backend API
}

// Load the templates dynamically from the server
function loadTemplates() {
    fetch('/api/templates')
        .then(response => response.json())
        .then(data => {
            const templateList = document.querySelector('.template-list');
            templateList.innerHTML = ''; // Clear the existing list
            data.forEach(template => {
                const templateItem = document.createElement('li');
                templateItem.innerHTML = `
                    ${template.subject}
                    <div>
                        <button class="delete-btn" onclick="deleteTemplate(${template.id})">Delete</button>
                        <button class="edit-btn" onclick="editTemplate(${template.id})">Edit</button>
                    </div>
                `;
                templateList.appendChild(templateItem);
            });
        })
        .catch(error => console.error('Error:', error));
}

// Open the form for creating a new template
function openForm() {
    document.getElementById('template-form-container').style.display = 'block';
    document.getElementById('template-form').reset();  // Clear any existing data in the form
    delete document.getElementById('template-form').dataset.templateId; // Clear any existing template ID
}

// Close the form
function closeForm() {
    document.getElementById('template-form-container').style.display = 'none';
}

// Handle saving the template (either creating a new one or editing an existing one)
function saveTemplate() {
    const templateId = document.getElementById('template-form').dataset.templateId;
    const method = templateId ? 'PUT' : 'POST';
    const url = templateId ? `/api/templates/${templateId}` : '/api/templates';

    const templateData = {
        subject: document.getElementById('subject').value,
        body: document.getElementById('body').value
    };

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(templateData),
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        loadTemplates(); // Reload the template list after saving
        closeForm();
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while saving the template');
    });
}

// Handle editing a template
function editTemplate(id) {
    fetch(`/api/templates/${id}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('subject').value = data.subject;
            document.getElementById('body').value = data.body;
            document.getElementById('template-form').dataset.templateId = id;
            openForm();
        })
        .catch(error => console.error('Error:', error));
}

// Handle deleting a template
function deleteTemplate(id) {
    if (confirm('Are you sure you want to delete this template?')) {
        fetch(`/api/templates/${id}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                loadTemplates(); // Reload the template list after deletion
            })
            .catch(error => console.error('Error:', error));
    }
}
