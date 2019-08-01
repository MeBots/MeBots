// There is no elegance here. Only sleep deprivation and regret.
let avatarInput = document.getElementById('avatar_url'), avatarPreview;
function previewAvatar() {
    avatarPreview.style.backgroundImage = 'url(' + avatarInput.value + ')';
}
if (avatarInput) {
    avatarPreview = document.createElement('div');
    avatarPreview.id = 'avatar_preview';
    previewAvatar();
    avatarInput.oninput = previewAvatar;
}
