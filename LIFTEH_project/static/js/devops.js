function loadDeveloperInfo() {
  const modal = new bootstrap.Modal(document.getElementById('objectModal'));

  // Данные о разработчике
  const developerData = {
    name: "Konstantin Brajcev",
    position: "CEO & Chief Engineer | FullStack Developer | Progect manager",
    email: "kastettb@gmail.com",
    address: "109-23, Belickaya st., Gomel, Belarus, 246042",
    phone: "+375 (29) 158-68-50",
    telegram: "@Constantine_al",
    linkedin: "linkedin.com/in/konstantinbrajcev",
    github: "KonstantinBrajcev",
    technologies: ["Python", "Django", "JavaScript", "Bootstrap", "SQLite", "HTML/CSS", "API", "CI/CD", "GitHub"],
    description: "This software solution is engineered to facilitate work progress monitoring, vehicle location tracking, task creation and assignment to personnel, and operational coordination of maintenance activities within organizations specializing in technical maintenance, emergency restoration, installation, and commissioning services."
  };

  // Формируем HTML контент
  const htmlContent = `
        <div class="text-center">
            <div class="mb-3">
                <i class="bi bi-person-badge display-4 text-info"></i>
            </div>
            <h3>${developerData.name}</h3>
            <p class="text-muted">${developerData.position}</p>
            <i>${developerData.description}</i>
            <div class="mt-4 text-start">
                <h5>Контакты:</h5>
                <ul class="list-unstyled">
                    <li>
                      <img src="/static/ico/envelope-fill.svg" alt="E:mail" class="me-2" style="width: 16px; height: 16px;">
                      ${developerData.email}</li>
                    <li>
                      <img src="/static/ico/telephone-fill.svg" alt="Phone" class="me-2" style="width: 16px; height: 16px;">
                      ${developerData.phone}</li>
                    <li>
                      <img src="/static/ico/whatsapp.svg" alt="Whatsapp" class="me-2" style="width: 16px; height: 16px;">
                      ${developerData.phone}</li>
                    <li>
                      <img src="/static/ico/telegram.svg" alt="Telegram" class="me-2" style="width: 16px; height: 16px;">
                      ${developerData.telegram}</li>
                    <li>
                      <img src="/static/ico/github.svg" alt="GitHub" class="me-2" style="width: 16px; height: 16px;">
                      ${developerData.github}</li>
                    <li>
                      <img src="/static/ico/linkedin.svg" alt="Linkedin" class="me-2" style="width: 16px; height: 16px;">
                      ${developerData.linkedin}</li>
                    <li>
                      <img src="/static/ico/geo-alt-fill.svg" alt="address" class="me-2" style="width: 16px; height: 16px;">
                      ${developerData.address}</li>
                </ul>

                <h5>Технологии проекта:</h5>
                <div class="d-flex flex-wrap gap-2">
                    ${developerData.technologies.map(tech => `<span class="badge bg-primary mb-1">${tech}</span>`).join('')}
                </div>
            </div>
        </div>
    `;

  // Обновляем заголовок и контент модального окна
  document.getElementById('modalTitle').textContent = 'О разработчике';
  document.getElementById('modalFormContent').innerHTML = htmlContent;

  // Показываем модальное окно
  modal.show();
}