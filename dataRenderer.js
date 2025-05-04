document.addEventListener("DOMContentLoaded", async () => {
  const upcomingContainer = document.getElementById("upcomingEventsList");
  const previousContainer = document.getElementById("previousEventsList");
  const partnersContainer = document.getElementById("partnersList");
  const teamContainer = document.getElementById("teamList");

  // Fetch JSON data
  const [upcomingEvents, previousEvents, team, partners] = await Promise.all([
    fetch('./data/upcomingevents.json').then(res => res.json()).catch(() => []),
    fetch('./data/previousevents.json').then(res => res.json()).catch(() => []),
    fetch('./data/team.json').then(res => res.json()).catch(() => []),
    fetch('./data/partners.json').then(res => res.json()).catch(() => []),
  ]);

  function renderEvents(container, events) {
    container.innerHTML = "";
    if (events.length === 0) {
      const noEventsMessage = document.createElement("p");
      noEventsMessage.textContent = "No events available.";
      container.appendChild(noEventsMessage);
      return;
    }

    events.forEach(event => {
      const card = document.createElement("div");
      card.className = "p-6 border rounded-lg shadow";
      card.innerHTML = `
        <a href="${event.link}" target="_blank">
          <h3 class="text-xl font-semibold mb-2">${event.title}</h3>
          <p class="mb-2 text-sm text-gray-600">${event.date}</p>
        </a>
      `;
      container.appendChild(card);
    });
  }

  function renderTeam(container, team) {
    container.innerHTML = "";
    team.forEach(member => {
      const card = document.createElement("div");
      card.innerHTML = `
        <a href="${member.link}" target="_blank">
          <img src="${member.foto}" class="rounded-full mx-auto mb-2 w-24 h-24 object-cover" alt="${member.nome}">
          <h3 class="font-semibold">${member.nome}</h3>
          <p class="text-sm text-gray-600">${member.cargo}</p>
        </a>
      `;
      container.appendChild(card);
    });
  }

  function renderPartners(container, partners) {
    container.innerHTML = "";
    partners.forEach(partner => {
      const card = document.createElement("div");
      card.innerHTML = `
        <a href="${partner.link}" target="_blank">
          <img src="${partner.foto}" alt="${partner.nome}" class="mx-auto mb-10 max-h-20 object-contain">
          <p class="text-sm text-gray-600">${partner.nome}</p>
        </a>
      `;
      container.appendChild(card);
    });
  }

  renderEvents(upcomingContainer, upcomingEvents);
  renderEvents(previousContainer, previousEvents);
  renderTeam(teamContainer, team);
  renderPartners(partnersContainer, partners);
});
