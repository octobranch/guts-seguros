/* GUTS Seguros: progressive enhancement. Content, navigation and ES/EN are static HTML. */
(() => {
 'use strict';
 const $=id=>document.getElementById(id);
 const language=document.body.dataset.language==='en'?'en':'es';
 const copy={
  es:{open:'Abrir menú',close:'Cerrar menú',subject:'Consulta de seguro | GUTS Seguros',hello:'Hola, equipo de GUTS Seguros.',name:'Nombre',email:'Correo de contacto',interest:'Me interesa',goal:'Mi objetivo',bye:'Me gustaría recibir orientación sobre esta opción. Gracias.',ready:'Consulta preparada. Revisa el mensaje y abre tu correo para enviarlo.',copied:'Mensaje copiado. Puedes pegarlo en tu aplicación de correo.',fallback:'Selecciona y copia el mensaje para pegarlo en tu correo.',
   goals:{salud:['Empieza por conocer los gastos médicos mayores.','Revisa hospitales, deducible, coaseguro y condiciones de cobertura. El precio por sí solo no cuenta toda la historia.','seguro-gastos-medicos-mayores-cancun.html'],familia:['Conoce cómo funciona un seguro de vida.','Piensa en las personas que dependen de ti y en el respaldo económico que podrían necesitar.','seguro-de-vida-cancun.html'],metas:['Explora las opciones de protección y ahorro.','Define tu objetivo y el plazo para alcanzarlo. Revisa aportaciones, costos y condiciones de retiro.','seguro-de-ahorro-cancun.html'],empresa:['Conoce el seguro de persona clave.','Identifica quién es esencial para tu negocio y qué impacto tendría su pérdida en la operación.','seguro-persona-clave-cancun.html']}},
  en:{open:'Open menu',close:'Close menu',subject:'Insurance enquiry | GUTS Seguros',hello:'Hello, GUTS Seguros team.',name:'Name',email:'Contact email',interest:'I’m interested in',goal:'My goal',bye:'I would like advice about this option. Thank you.',ready:'Enquiry prepared. Review the message and open your email app to send it.',copied:'Message copied. You can paste it into your email app.',fallback:'Select and copy the message to paste it into your email app.',
   goals:{salud:['Start by exploring major medical insurance.','Review hospitals, deductibles, coinsurance and coverage terms. Price alone does not tell the whole story.','major-medical-insurance-cancun.html'],familia:['Explore how life insurance works.','Think about the people who depend on you and the financial support they might need.','life-insurance-cancun.html'],metas:['Explore protection and savings options.','Define your goal and timeframe. Review contributions, costs and withdrawal terms.','savings-insurance-cancun.html'],empresa:['Explore key person insurance.','Identify who is essential to your business and how their loss could affect operations.','key-person-insurance-cancun.html']}}
 }[language];
 document.documentElement.classList.add('ready');
 const menu=$('mobile-nav'),button=$('menu-toggle');
 function closeMenu(focus=false){if(!menu||!button)return;menu.hidden=true;button.setAttribute('aria-expanded','false');button.setAttribute('aria-label',copy.open);if(focus)button.focus();}
 if(menu&&button){
  button.addEventListener('click',()=>{const open=menu.hidden;menu.hidden=!open;button.setAttribute('aria-expanded',String(open));button.setAttribute('aria-label',open?copy.close:copy.open);});
  menu.addEventListener('click',event=>{if(event.target.closest('a'))closeMenu();});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!menu.hidden)closeMenu(true);});
  document.addEventListener('click',event=>{if(!menu.hidden&&!menu.contains(event.target)&&!button.contains(event.target))closeMenu();});
  const viewport=matchMedia('(max-width:800px)'),onChange=event=>{if(!event.matches)closeMenu();};
  if(typeof viewport.addEventListener==='function')viewport.addEventListener('change',onChange);
  else if(typeof viewport.addListener==='function')viewport.addListener(onChange);
 }
 const goals=$('goal-options');
 if(goals){
  const update=()=>{const selected=document.querySelector('input[name="goal"]:checked')?.value||'salud';const [title,description,href]=copy.goals[selected];$('goal-title').textContent=title;$('goal-description').textContent=description;$('goal-link').setAttribute('href',href);};
  goals.addEventListener('change',update);update();
 }
 const form=$('quote-form');let draft=null;
 if(form){
  form.hidden=false;
  const invalidate=()=>{draft=null;$('draft').hidden=true;};
  form.addEventListener('input',invalidate);form.addEventListener('change',invalidate);
  form.addEventListener('submit',event=>{
   event.preventDefault();if(!form.reportValidity())return;
   const name=$('name').value.trim();if(!name){$('name').value='';$('name').reportValidity();return;}
   const selected=$('insurance').selectedOptions[0];
   const lines=[copy.hello,'',copy.name+': '+name,copy.email+': '+$('email').value.trim(),copy.interest+': '+selected.textContent.trim()];
   const message=$('message').value.trim();if(message)lines.push('',copy.goal+': '+message);lines.push('',copy.bye);
   draft=lines.join('\n');$('draft-content').textContent=draft;
   $('draft-email').href='mailto:contacto@guts.mx?subject='+encodeURIComponent(copy.subject)+'&body='+encodeURIComponent(draft);
   $('draft').hidden=false;$('draft-status').textContent=copy.ready;
   $('draft-title').setAttribute('tabindex','-1');$('draft-title').focus({preventScroll:true});
   $('draft').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth',block:'nearest'});
  });
  $('copy-draft').addEventListener('click',async()=>{
   if(!draft)return;
   try{if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');await navigator.clipboard.writeText(draft);$('draft-status').textContent=copy.copied;}
   catch{const selection=window.getSelection(),range=document.createRange();range.selectNodeContents($('draft-content'));selection.removeAllRanges();selection.addRange(range);$('draft-status').textContent=copy.fallback;}
  });
 }
 if($('year'))$('year').textContent=new Date().getFullYear();
})();
