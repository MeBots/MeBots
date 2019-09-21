// There is no elegance here. Only sleep deprivation and regret.
function insertAfter(element, anchor) {
    anchor.parentNode.insertBefore(element, anchor.nextSibling);
}
let avatarInput = document.getElementById('avatar_url'), avatarPreview;
function previewAvatar() {
    avatarPreview.style.backgroundImage = 'url(' + avatarInput.value + '), url(/static/images/unknown.png)';
}
if (avatarInput) {
    avatarPreview = document.createElement('div');
    avatarPreview.id = 'avatar_preview';
    insertAfter(avatarPreview, avatarInput);
    previewAvatar();
    avatarInput.oninput = previewAvatar;
}

let nameInput = document.querySelector('input#name'),
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
