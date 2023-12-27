// 爬取目标 https://www.99.com.cn/wenda/ 的XHR请求代码

let xhr = new XMLHttpRequest();
xhr.open("GET", "https://www.99.com.cn/wenda/asklist?page=2&limit=5", true);
xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
        document.documentElement.innerHTML = xhr.responseText;
    }
};
xhr.send();
