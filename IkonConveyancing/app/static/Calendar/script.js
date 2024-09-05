document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: '/api/events',
        dateClick: function(info) {
            // Handle date click
            fetchEvents(info.dateStr);
        },
        eventClick: function(info) {
            // Handle event click
            showEventDetails(info.event);
        }
    });
    calendar.render();

    document.getElementById('add-event-form').addEventListener('submit', function(e) {
        e.preventDefault();
        addEvent();
    });
});

function fetchEvents(date) {
    // Fetch events for the selected date from the server
    fetch(`/api/events?date=${date}`)
        .then(response => response.json())
        .then(events => {
            updateEventList(events);
        });
}

function showEventDetails(event) {
    // Display event details (you can implement this as a modal or update a div)
    alert(`Event: ${event.title}\nTime: ${event.start}\nDescription: ${event.extendedProps.description}`);
}

function addEvent() {
    const title = document.getElementById('event-title').value;
    const datetime = document.getElementById('event-datetime').value;
    const description = document.getElementById('event-description').value;
    const priority = document.getElementById('event-priority').value;

    fetch('/api/events', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            title: title,
            start: datetime,
            description: description,
            priority: priority
        }),
    })
    .then(response => response.json())
    .then(data => {
        calendar.refetchEvents();
        document.getElementById('add-event-form').reset();
    });
}

function updateEventList(events) {
    const eventList = document.getElementById('today-events');
    eventList.innerHTML = '';
    events.forEach(event => {
        const li = document.createElement('li');
        li.textContent = `${event.title} - ${event.start}`;
        eventList.appendChild(li);
    });
}