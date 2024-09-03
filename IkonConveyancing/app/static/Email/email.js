// email.js

document.addEventListener('DOMContentLoaded', () => {
    const newTemplateButton = document.getElementById('new-template');
    const templateForm = document.getElementById('template-form');
    const deleteTemplateButton = document.getElementById('delete-template');
    const templateList = document.querySelector('.template-list');
    let currentTemplateId = null;

    newTemplateButton.addEventListener('click', () => {
        clearForm();
        currentTemplateId = null;
    });

    templateForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const formData = new FormData(templateForm);
        const data = {
            subject: formData.get('subject'),
            settlement_date: formData.get('settlement-date'),
            client_name: formData.get('client-name'),
            address: formData.get('address'),
            body: formData.get('body')
        };

        if (currentTemplateId) {
            updateTemplate(currentTemplateId, data);
        } else {
            createTemplate(data);
        }
    });

    deleteTemplateButton.addEventListener('click', () => {
        if (currentTemplateId) {
            deleteTemplate(currentTemplateId);
        }
    });

    function loadTemplates() {
        fetch('/api/templates')
            .then(response => response.json())
            .then(templates => {
                templateList.innerHTML = '';
                templates.forEach(template => {
                    const templateItem = document.createElement('div');
                    templateItem.classList.add('template-item');
                    templateItem.textContent = template.subject;
                    templateItem.addEventListener('click', () => {
                        loadTemplateDetails(template);
                    });
                    templateList.appendChild(templateItem);
                });
            });
    }

    function loadTemplateDetails(template) {
        currentTemplateId = template.id;
        templateForm.querySelector('#subject').value = template.subject;
        templateForm.querySelector('#settlement-date').value = template.settlement_date;
        templateForm.querySelector('#client-name').value = template.client_name;
        templateForm.querySelector('#address').value = template.address;
        templateForm.querySelector('#body').value = template.body;
    }

    function clearForm() {
        templateForm.reset();
    }

    function createTemplate(data) {
        fetch('/api/templates', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(result => {
                alert(result.message);
                loadTemplates();
                clearForm();
            });
    }

    function updateTemplate(id, data) {
        fetch(`/api/templates/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(result => {
                alert(result.message);
                loadTemplates();
                clearForm();
            });
    }

    function deleteTemplate(id) {
        fetch(`/api/templates/${id}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(result => {
                alert(result.message);
                loadTemplates();
                clearForm();
            });
    }

    loadTemplates();
});