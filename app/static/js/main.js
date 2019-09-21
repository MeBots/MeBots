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
