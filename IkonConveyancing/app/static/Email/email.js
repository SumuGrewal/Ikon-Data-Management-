document.addEventListener('DOMContentLoaded', function() {
    loadTemplates();

    document.getElementById('new-template').addEventListener('click', function() {
        clearForm();
    });

    document.getElementById('template-form').addEventListener('submit', function(event) {
        event.preventDefault();
        saveTemplate();
    });

    document.getElementById('delete-template').addEventListener('click', function() {
        const templateId = document.getElementById('template-form').dataset.templateId;
        if (templateId) {
            deleteTemplate(templateId);
        } else {
            alert('Please select a template first');
        }
    });

    document.getElementById('send-email').addEventListener('click', function() {
        sendEmail();
    });
});

function loadTemplates() {
    fetch('/api/templates')
        .then(response => response.json())
        .then(data => {
            const templateList = document.querySelector('.template-list');
            templateList.innerHTML = '';
            data.forEach(template => {
                const templateItem = document.createElement('div');
                templateItem.classList.add('template-item');
                templateItem.textContent = template.subject;
                templateItem.addEventListener('click', function() {
                    loadTemplateDetails(template.id);
                });
                templateList.appendChild(templateItem);
            });
        });
}

function loadTemplateDetails(id) {
    fetch(`/api/templates/${id}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('subject').value = data.subject;
            document.getElementById('settlement-date').value = data.settlement_date;
            document.getElementById('client-name').value = data.client_name;
            document.getElementById('address').value = data.address;
            document.getElementById('body').value = data.body;
            document.getElementById('recipient').value = ''; // Clear recipient field
            document.getElementById('template-form').dataset.templateId = id;
        });
}

function saveTemplate() {
    const templateId = document.getElementById('template-form').dataset.templateId;
    const method = templateId ? 'PUT' : 'POST';
    const url = templateId ? `/api/templates/${templateId}` : '/api/templates';

    const templateData = {
        subject: document.getElementById('subject').value,
        settlement_date: document.getElementById('settlement-date').value,
        client_name: document.getElementById('client-name').value,
        address: document.getElementById('address').value,
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
        loadTemplates();
        clearForm();
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while saving the template');
    });
}

function deleteTemplate(id) {
    if (confirm('Are you sure you want to delete this template?')) {
        fetch(`/api/templates/${id}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                loadTemplates();
                clearForm();
            });
    }
}

function sendEmail() {
    const templateId = document.getElementById('template-form').dataset.templateId;
    if (!templateId) {
        alert('Please select a template first');
        return;
    }

    const emailData = {
        subject: document.getElementById('subject').value,
        body: document.getElementById('body').value,
        recipient: document.getElementById('recipient').value
    };

    fetch('/api/send_email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(emailData),
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while sending the email');
    });
}

function clearForm() {
    document.getElementById('template-form').reset();
    delete document.getElementById('template-form').dataset.templateId;
}