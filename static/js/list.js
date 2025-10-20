document.addEventListener('DOMContentLoaded', function(){
  // Dropdown toggle
  const userBtn = document.getElementById('userDropdown');
  const userMenu = document.getElementById('userDropdownMenu');
  if(userBtn && userMenu){
    userBtn.addEventListener('click', (e)=>{ e.stopPropagation(); userMenu.classList.toggle('hidden'); });
    document.addEventListener('click', (e)=>{ if(!userMenu.contains(e.target) && e.target !== userBtn) userMenu.classList.add('hidden'); });
  }

  // Settings panel
  const settingsBtn = document.getElementById('open-settings');
  const settingsPanel = document.getElementById('settingsPanel');
  const themeToggle = document.getElementById('themeToggle');
  if(settingsBtn && settingsPanel){
    settingsBtn.addEventListener('click', (e)=>{ e.preventDefault(); e.stopPropagation(); settingsPanel.classList.toggle('hidden'); userMenu.classList.add('hidden'); });
    // initialize toggle from localStorage
    const saved = localStorage.getItem('theme') || (document.body.classList.contains('dark-theme') ? 'dark' : 'light');
    themeToggle.checked = saved === 'dark';
    document.body.classList.toggle('dark-theme', saved === 'dark');

    themeToggle.addEventListener('change', ()=> {
      const mode = themeToggle.checked ? 'dark' : 'light';
      document.body.classList.toggle('dark-theme', mode === 'dark');
      localStorage.setItem('theme', mode);
      document.cookie = `theme=${mode};path=/;max-age=${60*60*24*365}`;
    });
  }

  // Cerrar settingsPanel si se hace click fuera
  document.addEventListener('click', (e)=>{
    if(settingsPanel && !settingsPanel.classList.contains('hidden')){
      if(!settingsPanel.contains(e.target) && e.target !== settingsBtn){
        settingsPanel.classList.add('hidden');
      }
    }
  });

  // Modal logic
  const modal = document.getElementById('itemModal');
  const modalContent = document.getElementById('modalContent');
  const modalClose = document.getElementById('modalClose');
  const modalBackdrop = document.getElementById('modalBackdrop');

  function openModal(html){
    modalContent.innerHTML = html;
    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden','false');
    document.body.style.overflow = 'hidden';
  }
  function closeModal(){
    modal.classList.add('hidden');
    modal.setAttribute('aria-hidden','true');
    modalContent.innerHTML = '';
    document.body.style.overflow = '';
  }
  if(modalClose) modalClose.addEventListener('click', closeModal);
  if(modalBackdrop) modalBackdrop.addEventListener('click', closeModal);
  document.addEventListener('keydown', (e)=> { if(e.key === 'Escape') closeModal(); });

  // Click en tarjetas
  document.querySelectorAll('.entry-card').forEach(card=>{
    card.addEventListener('click', async ()=> {
      const id = card.dataset.id;
      if(!id) return;
      try {
        const resp = await fetch(`/entries/${id}/detail-json/`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
        if(!resp.ok) throw new Error('error');
        const data = await resp.json();
        const html = buildDetailHtml(data);
        openModal(html);
      } catch(e){
        openModal('<p>No se pudo cargar el detalle.</p>');
      }
    });
  });

  function buildDetailHtml(data){
    // Formulario editable dentro del modal
    return `
      <form id="entryEditForm" data-id="${data.id}">
        <div style="display:flex;gap:14px;align-items:flex-start;">
          ${data.image_url ? `<img src="${escapeHtml(data.image_url)}" alt="${escapeHtml(data.title)}" style="width:220px;max-height:320px;object-fit:cover;border-radius:6px;">` : ''}
          <div style="flex:1;">
            <label class="block font-semibold">Título</label>
            <input name="title" value="${escapeHtml(data.title)}" class="w-full px-3 py-2 border rounded mb-2">

            <label class="block font-semibold">Notas / Descripción</label>
            <textarea name="notes" class="w-full px-3 py-2 border rounded mb-2" rows="4">${escapeHtml(data.description)}</textarea>

            <div style="display:flex;gap:8px;">
              <div style="flex:1;">
                <label class="block font-semibold">Progreso actual</label>
                <input type="number" name="progress_current" value="${escapeHtml(data.progress_current)}" class="w-full px-3 py-2 border rounded">
              </div>
              <div style="width:110px;">
                <label class="block font-semibold">Total</label>
                <input type="number" name="progress_total" value="${escapeHtml(data.progress_total)}" class="w-full px-3 py-2 border rounded">
              </div>
              <div style="width:140px;">
                <label class="block font-semibold">Rating</label>
                <input type="number" name="rating" min="0" max="10" value="${escapeHtml(data.rating || '')}" class="w-full px-3 py-2 border rounded">
              </div>
            </div>

            <div style="display:flex;gap:8px;margin-top:8px;align-items:end;">
              <div style="flex:1;">
                <label class="block font-semibold">Estado</label>
                <select name="status" class="w-full px-3 py-2 border rounded">
                  <option value="pendiente" ${data.status === 'Pendiente' ? 'selected' : ''}>Pendiente</option>
                  <option value="en_curso" ${data.status === 'En Curso' ? 'selected' : ''}>En Curso</option>
                  <option value="terminado" ${data.status === 'Terminado' ? 'selected' : ''}>Terminado</option>
                  <option value="abandonado" ${data.status === 'Abandonado' ? 'selected' : ''}>Abandonado</option>
                </select>
              </div>

              <div style="width:160px;">
                <label class="block font-semibold">Plataforma</label>
                <input name="platform" value="${escapeHtml(data.platform || '')}" class="w-full px-3 py-2 border rounded">
              </div>
            </div>

            <div style="margin-top:12px;display:flex;gap:8px;">
              <button id="saveEntryBtn" type="button" class="bg-indigo-600 text-white px-4 py-2 rounded">Guardar cambios</button>
              <a href="${data.external_link || '#'}" target="_blank" class="text-sm text-gray-600 self-center">Ver enlace</a>
            </div>
          </div>
        </div>
      </form>
    `;
  }

  // Helper para CSRF
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  // Delegación: después de abrir modal, atachamos el handler al botón Guardar
  document.addEventListener('click', async function(e){
    if(e.target && e.target.id === 'saveEntryBtn'){
      const form = document.getElementById('entryEditForm');
      if(!form) return;
      const id = form.dataset.id;
      const formData = new FormData(form);
      const payload = {};
      formData.forEach((v,k) => { payload[k] = v; });

      try{
        const resp = await fetch(`/entries/${id}/update-json/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if(resp.ok && data.success){
          // refrescar la página o actualizar la ficha visual
          closeModal();
          location.reload();
        } else {
          alert('Error al guardar: ' + (data.error || 'Error desconocido'));
        }
      } catch(err){
        console.error(err);
        alert('Error al guardar. Revisa la consola.');
      }
    }
  });

  function escapeHtml(str){
    if(!str && str !== 0) return '';
    return String(str).replace(/[&<>"]|'/g, function(m){ return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]); });
  }
});
