document.getElementById('template-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(this);
    const data = {
        subject: formData.get('subject'),
        settlement_date: formData.get('settlement-date'),
        client_name: formData.get('client-name'),
        address: formData.get('address'),
        body: formData.get('body')
    };

    fetch('/api/templates', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Template created successfully') {
            alert('Template saved successfully');
            fetchAndDisplayTemplates(); // Refresh the template list
            // Clear the form fields
            this.reset();
        } else {
            alert('Error saving template: ' + data.message);
        }
    })
    .catch(error => console.error('Error:', error));
});

function fetchAndDisplayTemplates() {
    fetch('/api/templates')
        .then(response => response.json())
        .then(templates => {
            const templateList = document.querySelector('.template-list');
            templateList.innerHTML = ''; // Clear existing templates
            templates.forEach(template => {
                const templateElement = document.createElement('div');
                templateElement.textContent = template.subject;
                templateElement.classList.add('template-item');
                templateElement.dataset.id = template.id;
                templateList.appendChild(templateElement);
            });
        })
        .catch(error => console.error('Error fetching templates:', error));
}

// Call this function when the page loads
document.addEventListener('DOMContentLoaded', fetchAndDisplayTemplates);