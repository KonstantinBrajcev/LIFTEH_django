function openServiceModal(objectId) {
  const url = `/service/add/${objectId}/`;
  const title = 'Добавление обслуживания';

  if (typeof loadModalForm === 'function') {
    loadModalForm(url, title);
  } else {
    console.error('Функция loadModalForm не найдена');
  }
}

function openAvrModal(objectId) {
  const url = `/avr/add/${objectId}/`;
  const title = 'Добавление АВР';

  if (typeof loadModalForm === 'function') {
    loadModalForm(url, title);
  } else {
    console.error('Функция loadModalForm не найдена');
  }
}