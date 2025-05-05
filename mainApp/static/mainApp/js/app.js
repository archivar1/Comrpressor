const fileInput = document.getElementById('fileElem');
const uploadArea = document.getElementById('upload-area');
const form = document.getElementById('upload-form');
const errorMsg = document.getElementById('error-msg');

const allowedTypes = [
    'image/png',
    'image/jpeg',
    'image/webp',
    'image/svg+xml'
];

function validateFileType(file) {
    if (!allowedTypes.includes(file.type)) {
        showError('Недопустимый формат файла. Разрешены: PNG, JPEG, WebP, SVG.');
        return false;
    }
    return true;
}

function showError(message) {
    errorMsg.textContent = message;
    errorMsg.style.display = 'block';
}

function clearError() {
    errorMsg.textContent = '';
    errorMsg.style.display = 'none';
}

// Отправка формы при выборе файлов
fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        if (validateFileType(file)) {
            clearError();
            form.submit();
        }
    }
});

// Drag & Drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('highlight');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('highlight');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('highlight');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (validateFileType(file)) {
            clearError();
            fileInput.files = files;
            form.submit();
        }
    }
});

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('compression-form');
  const slider = document.getElementById('compression-slider');
  const input = document.getElementById('compression-value');
  let currentThumbnail = document.querySelector('.image-item');

  // Функция обновления данных при выборе изображения
  function selectImage(element) {
    const name = element.getAttribute('data-name');
    const url = element.getAttribute('data-url');
    const originalSize = element.getAttribute('data-size');
    const compressedSize = element.getAttribute('data-compressed');
    const percent = element.getAttribute('data-percent');
    const level = element.getAttribute('data-level');


    const titleEl = document.getElementById('image-title');
    if (titleEl) titleEl.textContent = name;


    document.getElementById('original-size').textContent = originalSize;
    document.getElementById('compressed-size').textContent = compressedSize;
    document.getElementById('compression-percent').textContent = `(${percent}%)`;


    document.getElementById('preview-img').src = url;
    form.image_url.value = url;
    form.image_name.value = name;
    form.original_size.value = originalSize;
    form.compressed_size.value = compressedSize;


    input.value = level;
    slider.value = level;
  }

  // Обработка клика по миниатюре
  document.querySelectorAll('.image-item').forEach(el => {
    el.addEventListener('click', () => {
      if (currentThumbnail) {
        currentThumbnail.classList.remove('selected');
      }
      el.classList.add('selected');
      currentThumbnail = el;

      selectImage(el);
    });
  });


  function syncSliderValue(v) {
    const val = Math.min(100, Math.max(10, v));
    input.value = val;
    slider.value = val;
  }

  slider.addEventListener('input', e => {
    input.value = e.target.value;
  });
  input.addEventListener('input', e => {
    syncSliderValue(e.target.value);
  });

  // Перехват отправки формы и AJAX-запрос
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = new FormData(form);
    data.set('compression_value', input.value);

    try {
      const resp = await fetch(form.action, {
        method: 'POST',
        body: data,
      });

      if (!resp.ok) {
        const err = await resp.json();
        alert(err.error || 'Ошибка при сжатии');
        return;
      }

      const json = await resp.json();
      const cleanUrl = json.image_url;
      const bustUrl = cleanUrl + '?_=' + Date.now();
      document.getElementById('preview-img').src = bustUrl;




      form.image_url.value = cleanUrl;
      document.getElementById('original-size').textContent = json.original_size;
      document.getElementById('compressed-size').textContent = json.compressed_size;
      document.getElementById('compression-percent').textContent = `(${json.compressed_rate}%)`;

      input.value = json.compression_level;
      slider.value = json.compression_level;


      if (currentThumbnail) {
        currentThumbnail.setAttribute('data-url', cleanUrl);
        currentThumbnail.setAttribute('data-size', json.original_size);
        currentThumbnail.setAttribute('data-compressed', json.compressed_size);
        currentThumbnail.setAttribute('data-percent', json.compressed_rate);
        currentThumbnail.setAttribute('data-level', json.compression_level);
        const thumbImg = currentThumbnail.querySelector('img');
        if (thumbImg) thumbImg.src = bustUrl;
      }
    } catch (err) {
      console.error(err);
      alert('Не удалось связаться с сервером');
    }
  });


  if (currentThumbnail) {
    selectImage(currentThumbnail);
  }
});
window.selectImage = selectImage;