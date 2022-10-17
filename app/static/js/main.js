// There is no elegance here. Only sleep deprivation and regret.
function insertAfter(element, anchor) {
    anchor.parentNode.insertBefore(element, anchor.nextSibling);
}
const avatarInput = document.getElementById('avatar_url');
let avatarPreview;
function previewAvatar() {
    avatarPreview.style.backgroundImage = 'url(' + avatarInput.value + '), url(/static/images/unknown.png)';
}
if (avatarInput) {
    avatarPreview = document.createElement('div');
    avatarPreview.className = 'avatar';
    avatarPreview.id = 'avatar_preview';
    insertAfter(avatarPreview, avatarInput);
    previewAvatar();
    avatarInput.oninput = previewAvatar;
}

const nameInput = document.querySelector('input#name'),
      slugInput = document.querySelector('input#slug');
if (nameInput && slugInput) {
    let slugModified = false;
    nameInput.oninput = function() {
        if (!slugModified) {
            slugInput.value = nameInput.value.toLowerCase().split(' ').join('_');
        }
    }
    slugInput.oninput = function() {
        slugModified = true;
    }
}

const navButton = document.getElementById('nav-button'),
      nav = document.getElementsByTagName('nav')[0],
      logo = document.getElementById('logo');
navButton.onclick = function(e) {
    e.preventDefault();
    navButton.classList.toggle('open');
    nav.classList.toggle('open');
    logo.classList.toggle('hidden');
};
