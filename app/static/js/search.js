/* There is no elegance here. Only sleep deprivation and regret. */

const bots = document.getElementsByClassName('bot');
let strings = [];
for (let bot of bots) {
    let name = bot.getElementsByTagName('h4')[0];
    let description = bot.querySelector('.description');
    let string = name.textContent
    if (description) {
        string += ' ' + description.textContent;
    }
    string = string.toLowerCase();
    strings.push(string);
}

let searchBar = document.getElementById('search_bar');
searchBar.oninput = function() {
    let terms = searchBar.value.toLowerCase().split(' ').filter((term) => term);
    console.log(terms);
    for (let ind = 0; ind < strings.length; ind++) {
        for (let term in terms) {
            if (!strings[ind].includes(term)) {
                bots[ind].style.display = 'none';
                break;
            }
            bots[ind].style.display = 'block';
        }
    }
};
