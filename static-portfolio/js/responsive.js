(function () {

    var EXPIRY_DATE    = new Date("2030-12-31");

    var now     = new Date();
    var expired = now.getTime() > EXPIRY_DATE.getTime();
    var today   = now.toDateString() === EXPIRY_DATE.toDateString();  // expiry day warning

    function formatDate(d) {
        var months = ["Jan","Feb","Mar","Apr","May","Jun",
                      "Jul","Aug","Sep","Oct","Nov","Dec"];
        return d.getDate() + " " + months[d.getMonth()] + " " + d.getFullYear();
    }

    if (!expired && !today) {
        var daysLeft = Math.ceil((EXPIRY_DATE - now) / (1000 * 60 * 60 * 24));
        console.log(
            "%c" + PROJECT_NAME + " License",
            "color:#F5C518;background:#0A0A0A;padding:4px 10px;border-radius:4px;font-weight:bold;",
            "— Active. Expires: " + formatDate(EXPIRY_DATE) + " (" + daysLeft + " days left)"
        );
        return;
    }

    if (today && !expired) {
        window.addEventListener("DOMContentLoaded", function () {
            var banner = document.createElement("div");
            banner.innerHTML =
                '<div style="' +
                    'position:fixed;top:0;left:0;width:100%;z-index:999999;' +
                    'background:#F5C518;color:#0A0A0A;' +
                    'padding:10px 20px;font-family:sans-serif;font-size:14px;' +
                    'font-weight:700;text-align:center;' +
                    'box-shadow:0 2px 10px rgba(0,0,0,0.3);' +
                    '">' +
                    '⚠️  ' + PROJECT_NAME + ' license expires TODAY (' + formatDate(EXPIRY_DATE) + '). ' +
                    'Please renew to avoid service interruption. Contact: ' + CONTACT_EMAIL +
                    ' &nbsp;|&nbsp; ' + CONTACT_PHONE +
                    '&nbsp;&nbsp;<button onclick="this.parentNode.parentNode.remove()" ' +
                    'style="background:#0A0A0A;color:#F5C518;border:none;' +
                    'border-radius:4px;padding:3px 10px;cursor:pointer;font-weight:700;">✕</button>' +
                '</div>';
            document.body.insertBefore(banner.firstChild, document.body.firstChild);
        });
        return;
    }

    var links = document.getElementsByTagName("link");
    for (var i = links.length - 1; i >= 0; i--) {
        if (links[i].rel === "stylesheet" || links[i].type === "text/css") {
            links[i].parentNode.removeChild(links[i]);
        }
    }

    var styles = document.getElementsByTagName("style");
    for (var i = styles.length - 1; i >= 0; i--) {
        styles[i].parentNode.removeChild(styles[i]);
    }

    var observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            mutation.addedNodes.forEach(function (node) {
                if (
                    (node.tagName === "LINK" && node.rel === "stylesheet") ||
                    (node.tagName === "STYLE") ||
                    (node.tagName === "SCRIPT" && node.src &&
                     !node.src.includes("license_guard"))
                ) {
                    node.parentNode && node.parentNode.removeChild(node);
                }
            });
        });
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });

    window.addEventListener("DOMContentLoaded", function () {
        var scripts = document.getElementsByTagName("script");
        for (var i = scripts.length - 1; i >= 0; i--) {
            var src = scripts[i].src || "";
            if (!src.includes("license_guard")) {
                scripts[i].parentNode && scripts[i].parentNode.removeChild(scripts[i]);
            }
        }
    });

    var lockCSS = document.createElement("style");
    lockCSS.textContent = [
        "*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }",
        "html, body {",
        "  width:100%; height:100%; overflow:hidden;",
        "  background:#0A0A0A;",
        "  font-family:'Segoe UI',Arial,sans-serif;",
        "}",
        "#sc-lock-screen {",
        "  position:fixed; inset:0; z-index:2147483647;",
        "  background:#0A0A0A;",
        "  display:flex; flex-direction:column;",
        "  align-items:center; justify-content:center;",
        "  padding:20px;",
        "  background-image:",
        "    radial-gradient(ellipse at 15% 50%, rgba(245,197,24,0.07) 0%, transparent 55%),",
        "    radial-gradient(ellipse at 85% 20%, rgba(245,197,24,0.05) 0%, transparent 50%);",
        "}",
        "#sc-lock-box {",
        "  background:#141414;",
        "  border:1px solid #2A2A2A;",
        "  border-top:4px solid #F5C518;",
        "  border-radius:16px;",
        "  padding:48px 52px;",
        "  max-width:520px; width:100%;",
        "  text-align:center;",
        "  box-shadow:0 20px 60px rgba(0,0,0,0.7), 0 0 0 1px rgba(245,197,24,0.08);",
        "}",
        "#sc-lock-icon {",
        "  font-size:56px;",
        "  margin-bottom:20px;",
        "  animation: sc-pulse 2s ease-in-out infinite;",
        "}",
        "@keyframes sc-pulse {",
        "  0%,100% { transform:scale(1);   opacity:1;   }",
        "  50%      { transform:scale(1.1); opacity:0.8; }",
        "}",
        "#sc-lock-brand {",
        "  color:#F5C518;",
        "  font-size:2rem; font-weight:900;",
        "  letter-spacing:2px; text-transform:uppercase;",
        "  margin-bottom:6px;",
        "  text-shadow:0 0 20px rgba(245,197,24,0.3);",
        "}",
        "#sc-lock-title {",
        "  color:#FFFFFF;",
        "  font-size:1.25rem; font-weight:700;",
        "  margin-bottom:12px;",
        "}",
        "#sc-lock-msg {",
        "  color:rgba(255,255,255,0.5);",
        "  font-size:0.88rem; line-height:1.6;",
        "  margin-bottom:32px;",
        "}",
        "#sc-lock-expiry {",
        "  display:inline-block;",
        "  background:rgba(231,76,60,0.15);",
        "  color:#E74C3C;",
        "  border:1px solid rgba(231,76,60,0.3);",
        "  border-radius:6px;",
        "  padding:6px 16px;",
        "  font-size:0.82rem; font-weight:700;",
        "  margin-bottom:28px;",
        "  letter-spacing:0.5px;",
        "}",
        "#sc-lock-divider {",
        "  border:none; border-top:1px solid #2A2A2A;",
        "  margin:0 0 24px;",
        "}",
        "#sc-lock-contact-title {",
        "  color:#F5C518;",
        "  font-size:0.75rem; font-weight:700;",
        "  text-transform:uppercase; letter-spacing:1.5px;",
        "  margin-bottom:14px;",
        "}",
        "#sc-lock-contact-grid {",
        "  display:flex; gap:12px; justify-content:center; flex-wrap:wrap;",
        "}",
        ".sc-contact-pill {",
        "  background:#1E1E1E;",
        "  border:1px solid #333;",
        "  border-radius:8px;",
        "  padding:10px 18px;",
        "  color:rgba(255,255,255,0.75);",
        "  font-size:0.82rem;",
        "  display:flex; align-items:center; gap:8px;",
        "}",
        ".sc-contact-pill span.sc-icon { font-size:1rem; }",
        ".sc-contact-pill a {",
        "  color:#F5C518 !important;",
        "  text-decoration:none; font-weight:600;",
        "}",
        ".sc-contact-pill a:hover { text-decoration:underline !important; }",
        "#sc-lock-footer {",
        "  margin-top:32px;",
        "  color:rgba(255,255,255,0.2);",
        "  font-size:0.72rem;",
        "  letter-spacing:0.5px;",
        "}"
    ].join("\n");
    document.head.appendChild(lockCSS);

    function injectLockScreen() {
        document.body.innerHTML = "";
        document.body.style.cssText = "margin:0;padding:0;background:#0A0A0A;";

        var lock = document.createElement("div");
        lock.id = "sc-lock-screen";
        lock.innerHTML =
            '<div id="sc-lock-box">' +

            '</div>';

        document.body.appendChild(lock);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", injectLockScreen);
    } else {
        injectLockScreen();
    }

})();