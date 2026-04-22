if((typeof Shopify) === 'undefined'){ window.Shopify = {}; }
if((typeof Shopify.getCart) === 'undefined'){
  Shopify.getCart = function(callback, cart){
    if(!cart){
      return jQuery.getJSON('/cart.js', function(cart, textStatus, xhr){
        if((typeof callback) === 'function'){
          callback(cart, textStatus, xhr);
        } else {
          Shopify.onCartUpdate(cart);
        }
      });
    } else {
      if((typeof callback) === 'function'){
        callback(cart);
      } else if(typeof Shopify.onCartUpdate === 'function'){
        Shopify.onCartUpdate(cart);
      }
    }
  };
}

/*
* @license
* Pipeline Theme (c) Groupthought Themes
*
* The contents of this file should not be modified.
* add any minor changes to assets/custom.js
*
*/
!function(t, e, i, s, n, o, r, a, l, c, h, d, u) {
    "use strict";
    function p(t) {
        var e = Object.create(null);
        return t && Object.keys(t).forEach((function(i) {
            if ("default" !== i) {
                var s = Object.getOwnPropertyDescriptor(t, i);
                Object.defineProperty(e, i, s.get ? s : {
                    enumerable: !0,
                    get: function() {
                        return t[i]
                    }
                })
            }
        }
        )),
        e.default = t,
        Object.freeze(e)
    }
    var m = p(o);
    function y(t) {
        const e = t.querySelectorAll("[data-modal]")
          , i = document.querySelector("[data-modal-container]");
        e.forEach((t=>{
            i.querySelector(`[id="${t.id}"]`) || i.appendChild(t)
        }
        ))
    }
    window.theme = window.theme || {},
    window.theme.sizes = {
        small: 480,
        medium: 768,
        large: 990,
        widescreen: 1400
    },
    window.theme.keyboardKeys = {
        TAB: 9,
        ENTER: 13,
        ESCAPE: 27,
        SPACE: 32,
        LEFTARROW: 37,
        RIGHTARROW: 39
    };
    const f = ["neighbor--white", "neighbor--light", "neighbor--dark", "neighbor--black"];
    function g(t) {
        t.querySelectorAll("shopify-section").forEach((t=>{
            t.classList.remove(f)
        }
        )),
        t.querySelectorAll(".bg--neutral").forEach((t=>{
            t.parentElement.classList.add("neighbor--white")
        }
        )),
        t.querySelectorAll(".bg--accent").forEach((t=>{
            t.parentElement.classList.add("neighbor--light")
        }
        )),
        t.querySelectorAll(".bg--invert").forEach((t=>{
            t.parentElement.classList.add("neighbor--dark")
        }
        )),
        t.querySelectorAll(".bg--invert--accent").forEach((t=>{
            t.parentElement.classList.add("neighbor--black")
        }
        ))
    }
    function w(t) {
        t.querySelectorAll(".float__wrapper").forEach((t=>{
            const e = t.querySelector("label")
              , i = t.querySelector("input, textarea");
            e && i.addEventListener("keyup", (t=>{
                "" !== t.target.value ? e.classList.add("label--float") : e.classList.remove("label--float")
            }
            )),
            i && i.value && i.value.length && e.classList.add("label--float")
        }
        ))
    }
    function v(t) {
        t.querySelectorAll(".errors").forEach((t=>{
            t.setAttribute("tabindex", "0"),
            t.setAttribute("aria-live", "assertive"),
            t.setAttribute("role", "alert")
        }
        ))
    }
    function b(t) {
        document.addEventListener("theme:resize", S.bind(null, t)),
        S(t)
    }
    function S(t) {
        window.innerWidth > window.theme.sizes.small && setTimeout((()=>{
            t.querySelectorAll(".lazypostload-desktop").forEach((t=>{
                t.style.visibility = "visible"
            }
            ))
        }
        ), 2e3)
    }
    function E() {
        const t = {};
        return t.windowHeight = window.innerHeight,
        t.announcementHeight = k("#shopify-section-announcement"),
        t.footerHeight = k('[data-section-type*="footer"]'),
        t.menuHeight = k("[data-header-height]"),
        t.headerHeight = t.menuHeight + t.announcementHeight,
        t.logoHeight = function() {
            const t = k("[data-footer-logo]");
            return t > 0 ? t + 20 : 0
        }(),
        t
    }
    function L() {
        document.addEventListener("theme:resize", T),
        function() {
            const {windowHeight: t, announcementHeight: e, headerHeight: i, logoHeight: s, menuHeight: n, footerHeight: o} = E();
            document.documentElement.style.setProperty("--full-screen", t + "px"),
            document.documentElement.style.setProperty("--three-quarters", .75 * t + "px"),
            document.documentElement.style.setProperty("--two-thirds", .66 * t + "px"),
            document.documentElement.style.setProperty("--one-half", .5 * t + "px"),
            document.documentElement.style.setProperty("--one-third", .33 * t + "px"),
            document.documentElement.style.setProperty("--one-fifth", .2 * t + "px"),
            document.documentElement.style.setProperty("--menu-height", n + "px"),
            document.documentElement.style.setProperty("--announcement-height", e + "px"),
            document.documentElement.style.setProperty("--header-height", i + "px"),
            document.documentElement.style.setProperty("--footer-height", o + "px"),
            document.documentElement.style.setProperty("--content-full", t - i - s / 2 + "px"),
            document.documentElement.style.setProperty("--content-min", t - i - o + "px"),
            document.documentElement.style.setProperty("--scrollbar-width", window.innerWidth - document.documentElement.clientWidth + "px")
        }()
    }
    function T() {
        const {windowHeight: t, announcementHeight: e, headerHeight: i, logoHeight: s, menuHeight: n, footerHeight: o} = E();
        document.documentElement.style.setProperty("--menu-height", n + "px"),
        document.documentElement.style.setProperty("--announcement-height", e + "px"),
        document.documentElement.style.setProperty("--header-height", i + "px"),
        document.documentElement.style.setProperty("--footer-height", o + "px"),
        document.documentElement.style.setProperty("--content-full", t - i - s / 2 + "px"),
        document.documentElement.style.setProperty("--content-min", t - i - o + "px")
    }
    function k(t) {
        const e = document.querySelector(t);
        return e ? e.clientHeight : 0
    }
    function A(t, e) {
        let i = 64
          , s = 0;
        e.forEach((t=>{
            if (t.offsetHeight > s) {
                const e = parseInt(window.getComputedStyle(t).marginTop) + parseInt(window.getComputedStyle(t).marginBottom);
                e > i && (i = e),
                s = t.offsetHeight
            }
        }
        ));
        const n = t.querySelectorAll("[data-overflow-background]");
        [t, ...n].forEach((t=>{
            t.style.setProperty("min-height", `calc(${s + i}px + var(--menu-height)`)
        }
        ))
    }
    function q(t) {
        if (window.innerWidth < window.theme.sizes.medium) {
            return void t.querySelectorAll("[data-overflow-frame]").forEach((t=>{
                const e = t.querySelectorAll("[data-overflow-content]");
                A(t, e)
            }
            ))
        }
        const e = 2 * parseInt(getComputedStyle(t).getPropertyValue("--outer"));
        let i = 0;
        const s = t.querySelectorAll("[data-overflow-frame]");
        t.querySelectorAll("[data-overflow-content]").forEach((t=>{
            t.offsetHeight > i && (i = t.offsetHeight)
        }
        ));
        [...s, ...t.querySelectorAll("[data-overflow-background]")].forEach((t=>{
            t.style.setProperty("min-height", i + e + "px")
        }
        )),
        t.style.setProperty("min-height", i + e + 2 + "px")
    }
    function x(t) {
        const e = t.querySelectorAll(".js-overflow-container");
        e && e.forEach((t=>{
            const e = t.querySelectorAll(".js-overflow-content");
            A(t, e),
            document.addEventListener("theme:resize", (()=>{
                A(t, e)
            }
            ))
        }
        ));
        const i = t.querySelectorAll("[data-overflow-wrapper]");
        i && i.forEach((t=>{
            q(t),
            document.addEventListener("theme:resize", (()=>{
                q(t)
            }
            ))
        }
        ))
    }
    function _(t, e) {
        let i;
        return (...s)=>{
            clearTimeout(i),
            i = setTimeout((()=>t.apply(this, s)), e)
        }
    }
    let P = window.pageYOffset
      , C = null
      , D = null
      , M = null
      , H = null
      , I = 0;
    function B(e) {
        let i = e.target;
        e.detail && e.detail instanceof Element && (i = e.detail),
        t.disableBodyScroll(i),
        document.documentElement.setAttribute("data-scroll-locked", "")
    }
    function $() {
        if (I = setTimeout((()=>{
            document.body.removeAttribute("data-drawer-closing")
        }
        ), 20),
        document.body.hasAttribute("data-drawer-closing"))
            return document.body.removeAttribute("data-drawer-closing"),
            void (I && clearTimeout(I));
        document.body.setAttribute("data-drawer-closing", ""),
        document.documentElement.removeAttribute("data-scroll-locked"),
        t.clearAllBodyScrollLocks()
    }
    window.addEventListener("resize", _((function() {
        document.dispatchEvent(new CustomEvent("theme:resize",{
            bubbles: !0
        }))
    }
    ), 50)),
    function() {
        let t;
        window.addEventListener("scroll", (function() {
            t && window.cancelAnimationFrame(t),
            t = window.requestAnimationFrame((function() {
                !function() {
                    const t = window.pageYOffset;
                    t > P ? (D = !0,
                    C = !1) : t < P ? (D = !1,
                    C = !0) : (C = null,
                    D = null),
                    P = t,
                    document.dispatchEvent(new CustomEvent("theme:scroll",{
                        detail: {
                            up: C,
                            down: D,
                            position: t
                        },
                        bubbles: !1
                    })),
                    C && !M && document.dispatchEvent(new CustomEvent("theme:scroll:up",{
                        detail: {
                            position: t
                        },
                        bubbles: !1
                    })),
                    D && !H && document.dispatchEvent(new CustomEvent("theme:scroll:down",{
                        detail: {
                            position: t
                        },
                        bubbles: !1
                    })),
                    H = D,
                    M = C
                }()
            }
            ))
        }
        ), {
            passive: !0
        }),
        window.addEventListener("theme:scroll:lock", B),
        window.addEventListener("theme:scroll:unlock", $)
    }(),
    window.addEventListener("load", (()=>{
        L(),
        w(document),
        v(document),
        y(document),
        g(document),
        x(document),
        b(document)
    }
    )),
    document.addEventListener("shopify:section:load", (t=>{
        const e = t.target;
        w(e),
        v(e),
        y(e),
        g(e),
        x(e),
        b(e)
    }
    )),
    document.addEventListener("shopify:section:reorder", (()=>{
        document.dispatchEvent(new CustomEvent("header:check",{
            bubbles: !1
        }))
    }
    ));
    const F = (t,e=!1,i="block")=>{
        t && (e ? t.style.removeProperty("display") : t.style.display = i)
    }
    ;
    function O(t) {
        this.status = t.status || null,
        this.headers = t.headers || null,
        this.json = t.json || null,
        this.body = t.body || null
    }
    O.prototype = Error.prototype;
    const W = {
        expires: 7,
        path: "/",
        domain: window.location.hostname
    };
    class j {
        constructor(t={}) {
            this.options = {
                ...W,
                ...t
            }
        }
        write(t) {
            document.cookie = `${this.options.name}=${t}; expires=${this.options.expires}; path=${this.options.path}; domain=${this.options.domain}`
        }
        read() {
            let t = [];
            const e = document.cookie.split("; ").find((t=>t.startsWith(this.options.name)));
            if (-1 !== document.cookie.indexOf("; ") && e) {
                const e = document.cookie.split("; ").find((t=>t.startsWith(this.options.name))).split("=")[1];
                null !== e && (t = e.split(","))
            }
            return t
        }
        destroy() {
            document.cookie = `${this.options.name}=null; expires=${this.options.expires}; path=${this.options.path}; domain=${this.options.domain}`
        }
        remove(t) {
            const e = this.read()
              , i = e.indexOf(t);
            -1 !== i && (e.splice(i, 1),
            this.write(e))
        }
    }
    const N = 4
      , z = 10
      , V = "[data-recently-viewed-products]"
      , R = "data-limit"
      , U = "[data-recent-link-tab]"
      , J = "[data-recent-wrapper]"
      , K = "[data-recently-viewed-tab]"
      , X = "[data-tabs-holder-scroll]"
      , Y = "[data-api-content]"
      , Q = "data-minimum"
      , G = {
        expires: 90,
        name: "shopify_recently_viewed"
    }
      , Z = []
      , tt = [];
    class et {
        constructor(t) {
            this.container = t.container,
            this.cookie = new j(G),
            this.wrapper = this.container.querySelector(V),
            null !== this.wrapper && (this.howManyToShow = parseInt(this.container.querySelector(J).getAttribute(R)) || N,
            this.minimum = parseInt(this.container.querySelector(J).getAttribute(Q)),
            this.recentViewedTab = this.container.querySelector(K),
            this.recentViewedLink = this.container.querySelector(U),
            this.tabsHolderScroll = this.container.querySelector(X),
            this.renderProducts())
        }
        renderProducts() {
            const t = this.cookie.read()
              , e = [];
            let i = 0;
            if (t.length > 0) {
                for (let s = 0; s < t.length; s++) {
                    const n = t[s];
                    if (tt.includes(n))
                        continue;
                    const o = `${window.theme.routes.root_url}products/${n}?section_id=api-product-grid-item`;
                    if (e.push(o),
                    i++,
                    i === this.howManyToShow || i === t.length - 1)
                        break
                }
                if (e.length > 0 && e.length >= this.minimum) {
                    this.container.classList.remove("hide"),
                    this.recentViewedLink && this.recentViewedLink.previousElementSibling && this.tabsHolderScroll.classList.remove("hide");
                    const t = e.map((t=>fetch(t, {
                        mode: "no-cors"
                    }).then(this.handleErrors)))
                      , i = [];
                    Promise.allSettled(t).then((t=>Promise.all(t.map((async t=>{
                        "fulfilled" === t.status && i.push(await t.value.text())
                    }
                    ))))).then((()=>{
                        i.forEach((t=>{
                            const e = document.createElement("div")
                              , i = document.createElement("div");
                            e.innerHTML = t,
                            i.classList.add("product-grid-slide"),
                            i.innerHTML = e.querySelector(Y).innerHTML,
                            this.wrapper.appendChild(i)
                        }
                        ))
                    }
                    )).then((()=>{
                        F(this.wrapper, !0),
                        this.container.dispatchEvent(new CustomEvent("recent-products:added",{
                            bubbles: !0
                        }))
                    }
                    ))
                } else if (this.recentViewedTab) {
                    const t = Array.prototype.filter.call(this.recentViewedTab.parentNode.children, (t=>t !== this.recentViewedTab)).length > 1;
                    this.recentViewedLink && this.recentViewedLink.previousElementSibling && this.tabsHolderScroll.classList.add("hide"),
                    t || this.container.classList.add("hide")
                } else
                    this.container.classList.add("hide")
            }
        }
        handleErrors(t) {
            return t.ok ? t : t.text().then((function(e) {
                throw new O({
                    status: t.statusText,
                    headers: t.headers,
                    text: e
                })
            }
            ))
        }
    }
    class it {
        constructor(t) {
            this.handle = t,
            this.cookie = new j(G),
            void 0 !== this.handle && (tt.push(this.handle),
            this.updateCookie())
        }
        updateCookie() {
            let t = this.cookie.read();
            const e = t.indexOf(this.handle);
            -1 === e ? (t.unshift(this.handle),
            t = t.splice(0, z)) : (t.splice(e, 1),
            t.unshift(this.handle)),
            this.cookie.write(t)
        }
    }
    const st = {
        onLoad() {
            Z[this.id] = new et(this)
        }
    }
      , nt = "[data-address-wrapper]"
      , ot = "[data-new-address-form]"
      , rt = "[new-address-form-inner]"
      , at = ".address-new-toggle"
      , lt = ".address-edit-toggle"
      , ct = ".address-delete"
      , ht = "hide"
      , dt = "data-form-id"
      , ut = "data-confirm-message"
      , pt = "Are you sure you wish to delete this address?"
      , mt = "#EditAddress"
      , yt = "AddressCountryNew"
      , ft = "AddressProvinceNew"
      , gt = "AddressProvinceContainerNew"
      , wt = ".address-country-option"
      , vt = "AddressCountry"
      , bt = "AddressProvince"
      , St = "AddressProvinceContainer";
    class Et {
        constructor(t) {
            this.section = t,
            this.addressNewForm = this.section.querySelector(ot),
            this.init()
        }
        init() {
            if (this.addressNewForm) {
                const t = this.section
                  , e = this.addressNewForm.querySelector(rt);
                this.customerAddresses();
                const i = t.querySelectorAll(at);
                i.length && i.forEach((t=>{
                    t.addEventListener("click", (function() {
                        e.classList.toggle(ht)
                    }
                    ))
                }
                ));
                const s = t.querySelectorAll(lt);
                s.length && s.forEach((e=>{
                    e.addEventListener("click", (function() {
                        const e = this.getAttribute(dt);
                        t.querySelector(`${mt}_${e}`).classList.toggle(ht)
                    }
                    ))
                }
                ));
                const n = t.querySelectorAll(ct);
                n.length && n.forEach((t=>{
                    t.addEventListener("click", (function() {
                        const t = this.getAttribute(dt)
                          , e = this.getAttribute(ut);
                        confirm(e || pt) && Shopify.postLink("/account/addresses/" + t, {
                            parameters: {
                                _method: "delete"
                            }
                        })
                    }
                    ))
                }
                ))
            }
        }
        customerAddresses() {
            Shopify.CountryProvinceSelector && new Shopify.CountryProvinceSelector(yt,ft,{
                hideElement: gt
            });
            this.section.querySelectorAll(wt).forEach((t=>{
                const e = t.getAttribute(dt)
                  , i = `${vt}_${e}`
                  , s = `${bt}_${e}`
                  , n = `${St}_${e}`;
                new Shopify.CountryProvinceSelector(i,s,{
                    hideElement: n
                })
            }
            ))
        }
    }
    const Lt = document.querySelector(nt);
    Lt && new Et(Lt),
    document.querySelector("#RecoverPassword") && function() {
        var t = {
            recoverPasswordForm: "#RecoverPassword",
            hideRecoverPasswordLink: "#HideRecoverPasswordLink"
        };
        function e(t) {
            t.preventDefault(),
            s()
        }
        function i() {
            "#recover" === window.location.hash && s()
        }
        function s() {
            var t = document.querySelector("#CustomerEmail").value;
            document.querySelector("#RecoverEmail").value = t,
            document.querySelector("#RecoverPasswordForm").classList.toggle("display-none"),
            document.querySelector("#CustomerLoginForm").classList.toggle("display-none")
        }
        function n() {
            document.querySelector(".reset-password-success") && document.querySelector("#ResetSuccess").classList.remove("display-none")
        }
        i(),
        n(),
        document.querySelector(t.recoverPasswordForm).addEventListener("click", e),
        document.querySelector(t.hideRecoverPasswordLink).addEventListener("click", e)
    }(),
    window.Shopify = window.Shopify || {},
    window.Shopify.theme = window.Shopify.theme || {},
    window.Shopify.theme.sections = window.Shopify.theme.sections || {},
    window.Shopify.theme.sections.registered = window.Shopify.theme.sections.registered || {},
    window.Shopify.theme.sections.instances = window.Shopify.theme.sections.instances || [];
    const Tt = window.Shopify.theme.sections.registered
      , kt = window.Shopify.theme.sections.instances
      , At = "data-section-id"
      , qt = "data-section-type";
    class xt {
        constructor(t=null, e=[]) {
            this.type = t,
            this.components = function(t) {
                if (void 0 !== t && "object" != typeof t || null === t)
                    throw new TypeError("Theme Sections: The components object provided is not a valid");
                return t
            }(e),
            this.callStack = {
                onLoad: [],
                onUnload: [],
                onSelect: [],
                onDeselect: [],
                onBlockSelect: [],
                onBlockDeselect: [],
                onReorder: []
            },
            e.forEach((t=>{
                for (const [e,i] of Object.entries(t)) {
                    const t = this.callStack[e];
                    Array.isArray(t) && "function" == typeof i ? t.push(i) : (console.warn(`Unregisted function: '${e}' in component: '${this.type}'`),
                    console.warn(i))
                }
            }
            ))
        }
        getStack() {
            return this.callStack
        }
    }
    class _t {
        constructor(t, e) {
            this.container = function(t) {
                if (!(t instanceof Element))
                    throw new TypeError("Theme Sections: Attempted to load section. The section container provided is not a DOM element.");
                if (null === t.getAttribute(At))
                    throw new Error("Theme Sections: The section container provided does not have an id assigned to the " + At + " attribute.");
                return t
            }(t),
            this.id = t.getAttribute(At),
            this.type = e.type,
            this.callStack = e.getStack();
            try {
                this.onLoad()
            } catch (t) {
                console.warn("Error in section: " + this.id),
                console.warn(this),
                console.warn(t)
            }
        }
        callFunctions(t, e=null) {
            this.callStack[t].forEach((t=>{
                const i = {
                    id: this.id,
                    type: this.type,
                    container: this.container
                };
                e ? t.call(i, e) : t.call(i)
            }
            ))
        }
        onLoad() {
            this.callFunctions("onLoad")
        }
        onUnload() {
            this.callFunctions("onUnload")
        }
        onSelect(t) {
            this.callFunctions("onSelect", t)
        }
        onDeselect(t) {
            this.callFunctions("onDeselect", t)
        }
        onBlockSelect(t) {
            this.callFunctions("onBlockSelect", t)
        }
        onBlockDeselect(t) {
            this.callFunctions("onBlockDeselect", t)
        }
        onReorder(t) {
            this.callFunctions("onReorder", t)
        }
    }
    function Pt(t, e) {
        if ("string" != typeof t)
            throw new TypeError("Theme Sections: The first argument for .register must be a string that specifies the type of the section being registered");
        if (void 0 !== Tt[t])
            throw new Error('Theme Sections: A section of type "' + t + '" has already been registered. You cannot register the same section type twice');
        Array.isArray(e) || (e = [e]);
        const i = new xt(t,e);
        return Tt[t] = i,
        Tt
    }
    function Ct(t, e) {
        t = It(t),
        void 0 === e && (e = document.querySelectorAll("[" + qt + "]")),
        e = Bt(e),
        t.forEach((function(t) {
            const i = Tt[t];
            void 0 !== i && (e = e.filter((function(e) {
                return !(Mt(e).length > 0) && (null !== e.getAttribute(qt) && (e.getAttribute(qt) !== t || (kt.push(new _t(e,i)),
                !1)))
            }
            )))
        }
        ))
    }
    function Dt(t) {
        Mt(t).forEach((function(t) {
            var e = kt.map((function(t) {
                return t.id
            }
            )).indexOf(t.id);
            kt.splice(e, 1),
            t.onUnload()
        }
        ))
    }
    function Mt(t) {
        var e = [];
        if (NodeList.prototype.isPrototypeOf(t) || Array.isArray(t))
            var i = t[0];
        if (t instanceof Element || i instanceof Element)
            Bt(t).forEach((function(t) {
                e = e.concat(kt.filter((function(e) {
                    return e.container === t
                }
                )))
            }
            ));
        else if ("string" == typeof t || "string" == typeof i) {
            It(t).forEach((function(t) {
                e = e.concat(kt.filter((function(e) {
                    return e.type === t
                }
                )))
            }
            ))
        }
        return e
    }
    function Ht(t) {
        for (var e, i = 0; i < kt.length; i++)
            if (kt[i].id === t) {
                e = kt[i];
                break
            }
        return e
    }
    function It(t) {
        return "*" === t ? t = Object.keys(Tt) : "string" == typeof t ? t = [t] : t.constructor === _t ? t = [t.prototype.type] : Array.isArray(t) && t[0].constructor === _t && (t = t.map((function(t) {
            return t.type
        }
        ))),
        t = t.map((function(t) {
            return t.toLowerCase()
        }
        ))
    }
    function Bt(t) {
        return NodeList.prototype.isPrototypeOf(t) && t.length > 0 ? t = Array.prototype.slice.call(t) : NodeList.prototype.isPrototypeOf(t) && 0 === t.length || null === t ? t = [] : !Array.isArray(t) && t instanceof Element && (t = [t]),
        t
    }
    function $t(t, e) {
        e = e || {},
        t.focus(),
        void 0 !== e.className && t.classList.add(e.className),
        t.addEventListener("blur", (function i(s) {
            s.target.removeEventListener(s.type, i),
            void 0 !== e.className && t.classList.remove(e.className)
        }
        ))
    }
    function Ft(t) {
        return t = t || {},
        Array.prototype.slice.call(document.querySelectorAll('a[href^="#"]')).filter((function(e) {
            if ("#" === e.hash || "" === e.hash)
                return !1;
            if (t.ignore && e.matches(t.ignore))
                return !1;
            if (i = e.hash.substr(1),
            null === document.getElementById(i))
                return !1;
            var i, s = document.querySelector(e.hash);
            return !!s && (e.addEventListener("click", (function() {
                $t(s, t)
            }
            )),
            !0)
        }
        ))
    }
    window.Shopify.designMode && (document.addEventListener("shopify:section:load", (function(t) {
        var e = t.detail.sectionId
          , i = t.target.querySelector("[" + At + '="' + e + '"]');
        null !== i && Ct(i.getAttribute(qt), i)
    }
    )),
    document.addEventListener("shopify:section:reorder", (function(t) {
        var e = t.detail.sectionId
          , i = t.target.querySelector("[" + At + '="' + e + '"]');
        "object" == typeof Mt(i)[0] && Dt(i),
        null !== i && Ct(i.getAttribute(qt), i)
    }
    )),
    document.addEventListener("shopify:section:unload", (function(t) {
        var e = t.detail.sectionId
          , i = t.target.querySelector("[" + At + '="' + e + '"]');
        "object" == typeof Mt(i)[0] && Dt(i)
    }
    )),
    document.addEventListener("shopify:section:select", (function(t) {
        var e = Ht(t.detail.sectionId);
        "object" == typeof e && e.onSelect(t)
    }
    )),
    document.addEventListener("shopify:section:deselect", (function(t) {
        var e = Ht(t.detail.sectionId);
        "object" == typeof e && e.onDeselect(t)
    }
    )),
    document.addEventListener("shopify:block:select", (function(t) {
        var e = Ht(t.detail.sectionId);
        "object" == typeof e && e.onBlockSelect(t)
    }
    )),
    document.addEventListener("shopify:block:deselect", (function(t) {
        var e = Ht(t.detail.sectionId);
        "object" == typeof e && e.onBlockDeselect(t)
    }
    )));
    var Ot = {};
    function Wt(t, e) {
        e = e || {};
        var i = function(t) {
            return Array.prototype.slice.call(t.querySelectorAll("[tabindex],[draggable],a[href],area,button:enabled,input:not([type=hidden]):enabled,object,select:enabled,textarea:enabled[data-focus-element]")).filter((function(t) {
                return Boolean(t.offsetWidth || t.offsetHeight || t.getClientRects().length)
            }
            ))
        }(t)
          , s = e.elementToFocus || t
          , n = i[0]
          , o = i[i.length - 1];
        jt(),
        Ot.focusin = function(e) {
            t !== e.target && !t.contains(e.target) && n && n.focus(),
            e.target !== t && e.target !== o && e.target !== n || document.addEventListener("keydown", Ot.keydown)
        }
        ,
        Ot.focusout = function() {
            document.removeEventListener("keydown", Ot.keydown)
        }
        ,
        Ot.keydown = function(e) {
            9 === e.keyCode && (e.target !== o || e.shiftKey || (e.preventDefault(),
            n.focus()),
            e.target !== t && e.target !== n || !e.shiftKey || (e.preventDefault(),
            o.focus()))
        }
        ,
        document.addEventListener("focusout", Ot.focusout),
        document.addEventListener("focusin", Ot.focusin),
        $t(s, e)
    }
    function jt() {
        document.removeEventListener("focusin", Ot.focusin),
        document.removeEventListener("focusout", Ot.focusout),
        document.removeEventListener("keydown", Ot.keydown)
    }
    const Nt = 'button, [href], select, textarea, [tabindex]:not([tabindex="-1"])';
    function zt(t) {
        const i = "data-popup-" + t;
        e.init({
            openTrigger: i,
            disableScroll: !0,
            onShow: (t,e,i)=>{
                i.preventDefault();
                const s = t.querySelector(Nt);
                Wt(t, {
                    elementToFocus: s
                })
            }
            ,
            onClose: (t,e,i)=>{
                i.preventDefault(),
                jt(),
                e.focus()
            }
        })
    }
    const Vt = "[data-toggle-password-modal]"
      , Rt = ".storefront-password-form .errors"
      , Ut = {};
    class Jt {
        constructor(t) {
            this.container = t.container,
            this.trigger = this.container.querySelector(Vt),
            this.errors = this.container.querySelector(Rt),
            this.init()
        }
        init() {
            zt("password"),
            this.errors && this.trigger.click()
        }
    }
    Pt("password", {
        onLoad() {
            Ut[this.id] = new Jt(this)
        }
    }),
    function() {
        var t = "#QrCode"
          , e = ".giftcard__code";
        const i = document.querySelector(t);
        if (i) {
            window.addEventListener("load", (function() {
                const t = i.getAttribute("data-identifier");
                new QRCode(i,{
                    text: t,
                    width: 120,
                    height: 120
                })
            }
            ))
        }
        const s = document.querySelector(e);
        if (s) {
            s.addEventListener("click", function() {
                var t = document.querySelector("#GiftCardDigits")
                  , e = "";
                if (document.body.createTextRange)
                    (e = document.body.createTextRange()).moveToElementText(t),
                    e.select();
                else if (window.getSelection) {
                    var i = window.getSelection();
                    (e = document.createRange()).selectNodeContents(t),
                    i.removeAllRanges(),
                    i.addRange(e)
                }
            }())
        }
    }();
    var Kt = {};
    const Xt = {
        onLoad() {
            Kt[this.id] = [];
            this.container.querySelectorAll("[data-parallax-wrapper]").forEach((t=>{
                const e = t.querySelector("[data-parallax-img]");
                Kt[this.id].push(new i(e,{
                    center: !0,
                    round: !0,
                    frame: t
                }))
            }
            ))
        },
        onUnload: function() {
            Kt[this.id].forEach((t=>{
                "function" == typeof t.destroy && t.destroy()
            }
            ))
        }
    };
    Pt("article", Xt);
    const Yt = "[data-ticker-scale]"
      , Qt = "[data-ticker-text]"
      , Gt = "data-clone"
      , Zt = "ticker--animated"
      , te = "ticker--unloaded"
      , ee = "ticker__comparitor"
      , ie = 1.63
      , se = 100;
    class ne {
        constructor(t, e=!1) {
            this.frame = t,
            this.stopClone = e,
            this.scale = this.frame.querySelector(Yt),
            this.text = this.frame.querySelector(Qt),
            this.comparitor = this.text.cloneNode(!0),
            this.comparitor.classList.add(ee),
            this.frame.appendChild(this.comparitor),
            this.scale.classList.remove(te),
            this.resizeEvent = _((()=>this.checkWidth()), 300),
            this.listen()
        }
        unload() {
            document.removeEventListener("theme:resize", this.resizeEvent)
        }
        listen() {
            document.addEventListener("theme:resize", this.resizeEvent),
            this.checkWidth()
        }
        checkWidth() {
            const t = 2 * window.getComputedStyle(this.frame).paddingLeft.replace("px", "");
            if (this.frame.clientWidth - t < this.comparitor.clientWidth || this.stopClone) {
                if (this.text.classList.add(Zt),
                1 === this.scale.childElementCount && (this.clone = this.text.cloneNode(!0),
                this.clone.setAttribute("aria-hidden", !0),
                this.clone.setAttribute(Gt, ""),
                this.scale.appendChild(this.clone),
                this.stopClone))
                    for (let t = 0; t < 10; t++) {
                        const t = this.text.cloneNode(!0);
                        t.setAttribute("aria-hidden", !0),
                        t.setAttribute(Gt, ""),
                        this.scale.appendChild(t)
                    }
                const t = this.text.clientWidth / se * ie;
                this.scale.style.setProperty("--animation-time", t + "s")
            } else {
                this.text.classList.add(Zt);
                let t = this.scale.querySelector(`[${Gt}]`);
                t && this.scale.removeChild(t),
                this.text.classList.remove(Zt)
            }
        }
    }
    const oe = "data-slider-speed"
      , re = "data-slide"
      , ae = "data-slide-index";
    class le {
        constructor(t, e) {
            this.container = t,
            this.slideshow = e;
            const i = this.slideshow.getAttribute(oe);
            this.speed = !!i && parseInt(i),
            this.slideshow && (this.flkty = null,
            this.init())
        }
        init() {
            const t = {
                initialIndex: 0,
                autoPlay: this.speed,
                contain: !0,
                pageDots: !1,
                adaptiveHeight: !0,
                wrapAround: !0,
                groupCells: !1,
                cellAlign: "left",
                freeScroll: !1,
                prevNextButtons: !0,
                draggable: !0,
                on: {
                    ready: ()=>{
                        setTimeout((()=>{
                            this.slideshow.dispatchEvent(new CustomEvent("theme:announcement:loaded",{
                                bubbles: !0,
                                detail: {
                                    slider: this
                                }
                            }))
                        }
                        ), 50)
                    }
                }
            };
            this.flkty = new s(this.slideshow,t),
            document.addEventListener("theme:resize", (()=>{
                this.flkty.resize()
            }
            ))
        }
        onUnload() {
            this.slideshow && this.flkty && (this.flkty.options.watchCSS = !1,
            this.flkty.destroy())
        }
        onBlockSelect(t) {
            if (!this.slideshow)
                return;
            const e = this.slideshow.querySelector(`[${re}="${t.detail.blockId}"]`);
            if (!e)
                return;
            const i = parseInt(e.getAttribute(ae));
            this.flkty.selectCell(i),
            this.flkty.stopPlayer()
        }
        onBlockDeselect() {
            this.flkty.playPlayer()
        }
    }
    const ce = "[data-cart-message]"
      , he = "data-cart-message"
      , de = "[data-left-to-spend]"
      , ue = "[data-cart-progress]"
      , pe = "is-hidden"
      , me = "is-success";
    class ye {
        constructor(t) {
            this.container = t,
            this.cartMessage = this.container.querySelectorAll(ce),
            this.cartMessage.length > 0 && this.init()
        }
        init() {
            this.cartFreeLimitShipping = 100 * Number(this.cartMessage[0].getAttribute("data-limit")),
            this.shippingAmount = 0,
            this.circumference = 28 * Math.PI,
            this.cartBarProgress(),
            this.listen()
        }
        listen() {
            document.addEventListener("theme:cart:change", function(t) {
                this.cart = t.detail.cart,
                this.render()
            }
            .bind(this))
        }
        render() {
            if (this.cart && this.cart.total_price) {
                const t = this.cart.total_price;
                this.freeShippingMessageHandle(t),
                this.cartMessage.length > 0 && (this.shippingAmount = t,
                this.updateProgress())
            }
        }
        freeShippingMessageHandle(t) {
            this.cartMessage.length > 0 && this.container.querySelectorAll(ce).forEach((e=>{
                const i = e.hasAttribute(he) && "true" === e.getAttribute(he) && 0 !== t ? me : pe;
                e.classList.toggle(i, t >= this.cartFreeLimitShipping)
            }
            ))
        }
        cartBarProgress(t=null) {
            this.container.querySelectorAll(ue).forEach((e=>{
                this.setProgress(e, null === t ? e.getAttribute("data-percent") : t)
            }
            ))
        }
        setProgress(t, e) {
            const i = this.circumference - e / 100 * this.circumference / 2;
            t.style.strokeDashoffset = i
        }
        updateProgress() {
            const t = this.shippingAmount / this.cartFreeLimitShipping * 100
              , e = n.formatMoney(this.cartFreeLimitShipping - this.shippingAmount, theme.moneyFormat);
            this.container.querySelectorAll(de).forEach((t=>{
                t.innerHTML = e.replace(".00", "")
            }
            )),
            this.cartBarProgress(t > 100 ? 100 : t)
        }
    }
    const fe = "[data-bar]"
      , ge = "[data-slide]"
      , we = "[data-ticker-frame]"
      , ve = "[data-announcement-slider]"
      , be = "data-slide"
      , Se = "[data-ticker-scale]"
      , Ee = "[data-ticker-text]"
      , Le = "data-target-referrer"
      , Te = "data-slide"
      , ke = "mobile"
      , Ae = "desktop"
      , qe = {};
    class xe {
        constructor(t) {
            this.container = t.container,
            this.barHolder = this.container.querySelector(fe),
            this.locationPath = location.href,
            this.slides = this.barHolder.querySelectorAll(ge),
            this.slider = this.barHolder.querySelector(ve),
            this.hasDeviceClass = "",
            new ye(this.container),
            this.init()
        }
        init() {
            this.removeAnnouncement(),
            this.slider ? this.slider && this.slides && this.slides.length > 1 ? this.initSliders() : this.initTickers() : this.initTickers(!0)
        }
        removeAnnouncement() {
            for (let t = 0; t < this.slides.length; t++) {
                const e = this.slides[t];
                e.hasAttribute(Le) && (-1 !== this.locationPath.indexOf(e.getAttribute(Le)) || window.Shopify.designMode || e.parentNode.removeChild(e))
            }
        }
        initSliders() {
            this.slider = new le(this.container,this.slider),
            this.slider.flkty.reposition(),
            this.barHolder.addEventListener("theme:announcement:loaded", (()=>{
                this.initTickers()
            }
            ))
        }
        initTickers(t=!1) {
            const e = this.barHolder.querySelector(we);
            new ne(e,t)
        }
        toggleTicker(t, e) {
            const i = document.querySelector(Se)
              , s = document.querySelector(`[${be}="${t.detail.blockId}"]`);
            e && s && (i.setAttribute("data-stop", ""),
            i.querySelectorAll(Ee).forEach((t=>{
                t.classList.remove("ticker--animated"),
                t.style.transform = `translate3d(${-(s.offsetLeft - s.clientWidth)}px, 0, 0)`
            }
            ))),
            !e && s && (i.querySelectorAll(Ee).forEach((t=>{
                t.classList.add("ticker--animated"),
                t.removeAttribute("style")
            }
            )),
            i.removeAttribute("data-stop"))
        }
        onBlockSelect(t) {
            if (this.slider && "function" == typeof this.slider.onBlockSelect)
                this.slider.onBlockSelect(t);
            else {
                document.querySelectorAll(`[${Te}="${t.detail.blockId}"]`).forEach((t=>{
                    t.classList.contains(ke) && (this.hasDeviceClass = ke),
                    t.classList.contains(Ae) && (this.hasDeviceClass = Ae),
                    "" !== this.hasDeviceClass && t.classList.remove(this.hasDeviceClass)
                }
                )),
                this.toggleTicker(t, !0)
            }
        }
        onBlockDeselect(t) {
            if (this.slider && "function" == typeof this.slider.onBlockDeselect)
                this.slider.onBlockDeselect(t);
            else {
                if ("" !== this.hasDeviceClass) {
                    document.querySelectorAll(`[${Te}="${t.detail.blockId}"]`).forEach((t=>{
                        t.classList.add(this.hasDeviceClass)
                    }
                    ))
                }
                this.toggleTicker(t, !1)
            }
        }
    }
    Pt("announcement", [{
        onLoad() {
            qe[this.id] = [],
            qe[this.id].push(new xe(this))
        },
        onBlockSelect(t) {
            qe[this.id].forEach((e=>{
                "function" == typeof e.onBlockSelect && e.onBlockSelect(t)
            }
            ))
        },
        onBlockDeselect(t) {
            qe[this.id].forEach((e=>{
                "function" == typeof e.onBlockSelect && e.onBlockDeselect(t)
            }
            ))
        }
    }]),
    Pt("blog", Xt);
    var _e = "[data-drawer]"
      , Pe = "[data-drawer-scrolls]"
      , Ce = "[data-drawer-underlay]"
      , De = "[data-stagger-animation]"
      , Me = "data-drawer-toggle"
      , He = 'button, [href], select, textarea, [tabindex]:not([tabindex="-1"])'
      , Ie = "drawer--visible"
      , Be = "display-none"
      , $e = {};
    class Fe {
        constructor(t) {
            this.drawer = t,
            this.drawerScrolls = this.drawer.querySelector(Pe),
            this.underlay = this.drawer.querySelector(Ce),
            this.key = this.drawer.dataset.drawer;
            const e = `[${Me}='${this.key}']`;
            this.buttons = document.querySelectorAll(e),
            this.staggers = this.drawer.querySelectorAll(De),
            this.connectToggle(),
            this.connectDrawer(),
            this.closers(),
            this.staggerChildAnimations()
        }
        unload() {}
        connectToggle() {
            this.buttons.forEach((t=>{
                t.addEventListener("click", function(t) {
                    t.preventDefault(),
                    this.drawer.dispatchEvent(new CustomEvent("theme:drawer:toggle",{
                        bubbles: !1
                    }))
                }
                .bind(this))
            }
            ))
        }
        connectDrawer() {
            this.drawer.addEventListener("theme:drawer:toggle", function() {
                this.drawer.classList.contains(Ie) ? this.drawer.dispatchEvent(new CustomEvent("theme:drawer:close",{
                    bubbles: !1
                })) : this.drawer.dispatchEvent(new CustomEvent("theme:drawer:open",{
                    bubbles: !1
                }))
            }
            .bind(this)),
            this.drawer.addEventListener("theme:drawer:close", this.hideDrawer.bind(this)),
            this.drawer.addEventListener("theme:drawer:open", this.showDrawer.bind(this))
        }
        staggerChildAnimations() {
            this.staggers.forEach((t=>{
                t.querySelectorAll(":scope > * > [data-animates]").forEach(((t,e)=>{
                    t.style.transitionDelay = 50 * e + 10 + "ms"
                }
                ))
            }
            ))
        }
        closers() {
            this.drawer.addEventListener("keyup", function(t) {
                t.which === window.theme.keyboardKeys.ESCAPE && (this.hideDrawer(),
                this.buttons[0].focus())
            }
            .bind(this)),
            this.underlay.addEventListener("click", function() {
                this.hideDrawer()
            }
            .bind(this))
        }
        showDrawer() {
            this.drawer.classList.remove(Be),
            setTimeout((()=>{
                this.buttons.forEach((t=>t.setAttribute("aria-expanded", !0))),
                this.drawer.classList.add(Ie),
                this.drawerScrolls.dispatchEvent(new CustomEvent("theme:scroll:lock",{
                    bubbles: !0
                }));
                const t = this.drawer.querySelector(He);
                Wt(this.drawer, {
                    elementToFocus: t
                })
            }
            ), 1)
        }
        hideDrawer() {
            this.buttons.forEach((t=>t.setAttribute("aria-expanded", !0))),
            this.drawer.classList.remove(Ie),
            this.drawerScrolls.dispatchEvent(new CustomEvent("theme:scroll:unlock",{
                bubbles: !0
            })),
            document.dispatchEvent(new CustomEvent("theme:sliderule:close",{
                bubbles: !1
            })),
            jt(),
            setTimeout((()=>{
                this.drawer.classList.contains(Ie) || this.drawer.classList.add(Be)
            }
            ), 800)
        }
    }
    const Oe = {
        onLoad() {
            $e[this.id] = [];
            this.container.querySelectorAll(_e).forEach((t=>{
                $e[this.id].push(new Fe(t))
            }
            ))
        },
        onUnload: function() {
            $e[this.id].forEach((t=>{
                "function" == typeof t.unload && t.unload()
            }
            ))
        }
    }
      , We = "#shopify-section-announcement"
      , je = "data-header-transparent"
      , Ne = "[data-header-wrapper] header"
      , ze = "js__header__stuck"
      , Ve = "js__header__stuck--animated"
      , Re = "js__header__stuck--trigger-animation"
      , Ue = "js__header__stuck__backdrop";
    let Je = {};
    class Ke {
        constructor(t) {
            this.wrapper = t,
            this.type = this.wrapper.dataset.headerSticky,
            this.transparent = this.wrapper.dataset.headerTransparent,
            this.sticks = "sticky" === this.type,
            this.animated = "directional" === this.type,
            this.currentlyStuck = !1,
            this.cls = this.wrapper.classList;
            const e = document.querySelector(We)
              , i = e ? e.clientHeight : 0
              , s = document.querySelector(Ne).clientHeight;
            this.blur = s + i,
            this.stickDown = s + i,
            this.stickUp = i,
            "false" !== this.wrapper.getAttribute(je) && (this.blur = i),
            this.sticks && (this.stickDown = i,
            this.scrollDownInit()),
            this.listen()
        }
        unload() {
            document.removeEventListener("theme:scroll", this.listen),
            document.removeEventListener("theme:scroll:up", this.scrollUpDirectional),
            document.removeEventListener("theme:scroll:down", this.scrollDownDirectional)
        }
        listen() {
            (this.sticks || this.animated) && document.addEventListener("theme:scroll", (t=>{
                t.detail.down ? (!this.currentlyStuck && t.detail.position > this.stickDown && this.stickSimple(),
                !this.currentlyBlurred && t.detail.position > this.blur && this.addBlur()) : (t.detail.position <= this.stickUp && this.unstickSimple(),
                t.detail.position <= this.blur && this.removeBlur())
            }
            )),
            this.animated && (document.addEventListener("theme:scroll:up", this.scrollUpDirectional.bind(this)),
            document.addEventListener("theme:scroll:down", this.scrollDownDirectional.bind(this)))
        }
        stickSimple() {
            this.animated && this.cls.add(Ve),
            this.cls.add(ze),
            this.wrapper.setAttribute(je, !1),
            this.currentlyStuck = !0
        }
        unstickSimple() {
            this.cls.remove(ze),
            this.wrapper.setAttribute(je, this.transparent),
            this.animated && this.cls.remove(Ve),
            this.currentlyStuck = !1
        }
        scrollDownInit() {
            window.scrollY > this.stickDown && this.stickSimple(),
            window.scrollY > this.blur && this.addBlur()
        }
        stickDirectional() {
            this.cls.add(Re)
        }
        unstickDirectional() {
            this.cls.remove(Re)
        }
        scrollDownDirectional() {
            this.unstickDirectional()
        }
        scrollUpDirectional() {
            window.scrollY <= this.stickDown ? this.unstickDirectional() : this.stickDirectional()
        }
        addBlur() {
            this.cls.add(Ue),
            this.currentlyBlurred = !0
        }
        removeBlur() {
            this.cls.remove(Ue),
            this.currentlyBlurred = !1
        }
    }
    const Xe = {
        onLoad() {
            Je = new Ke(this.container)
        },
        onUnload: function() {
            "function" == typeof Je.unload && Je.unload()
        }
    }
      , Ye = "data-hover-disclosure-toggle"
      , Qe = "[data-hover-disclosure]"
      , Ge = "[data-top-link]"
      , Ze = "[data-header-wrapper]"
      , ti = "[data-stagger]"
      , ei = "[data-stagger-first]"
      , ii = "[data-stagger-second]"
      , si = "[data-grid-item], [data-header-image]"
      , ni = "is-visible"
      , oi = "meganav--visible";
    let ri = {}
      , ai = {};
    class li {
        constructor(t) {
            this.disclosure = t,
            this.wrapper = t.closest(Ze),
            this.key = this.disclosure.id;
            const e = `[${Ye}='${this.key}']`;
            this.trigger = document.querySelector(e),
            this.link = this.trigger.querySelector(Ge),
            this.grandparent = this.trigger.classList.contains("grandparent"),
            this.trigger.setAttribute("aria-haspopup", !0),
            this.trigger.setAttribute("aria-expanded", !1),
            this.trigger.setAttribute("aria-controls", this.key),
            this.connectHoverToggle(),
            this.handleTablets(),
            this.staggerChildAnimations()
        }
        onBlockSelect(t) {
            this.disclosure.contains(t.target) && this.showDisclosure()
        }
        onBlockDeselect(t) {
            this.disclosure.contains(t.target) && this.hideDisclosure()
        }
        showDisclosure() {
            this.grandparent ? this.wrapper.classList.add(oi) : this.wrapper.classList.remove(oi),
            this.trigger.setAttribute("aria-expanded", !0),
            this.trigger.classList.add(ni),
            this.disclosure.classList.add(ni)
        }
        hideDisclosure() {
            this.disclosure.classList.remove(ni),
            this.trigger.classList.remove(ni),
            this.trigger.setAttribute("aria-expanded", !1),
            this.wrapper.classList.remove(oi)
        }
        staggerChildAnimations() {
            this.disclosure.querySelectorAll(ti).forEach(((t,e)=>{
                t.style.transitionDelay = 50 * e + 10 + "ms"
            }
            ));
            this.disclosure.querySelectorAll(ei).forEach(((t,e)=>{
                const i = 150 * e;
                t.style.transitionDelay = i + "ms",
                t.parentElement.querySelectorAll(ii).forEach(((t,e)=>{
                    const s = 20 * (e + 1);
                    t.style.transitionDelay = i + s + "ms"
                }
                ))
            }
            ));
            this.disclosure.querySelectorAll(si).forEach(((t,e)=>{
                t.style.transitionDelay = 80 * (e + 1) + "ms"
            }
            ))
        }
        handleTablets() {
            this.trigger.addEventListener("touchstart", function(t) {
                this.disclosure.classList.contains(ni) || (t.preventDefault(),
                this.showDisclosure())
            }
            .bind(this), {
                passive: !0
            })
        }
        connectHoverToggle() {
            this.trigger.addEventListener("mouseenter", this.showDisclosure.bind(this)),
            this.link.addEventListener("focus", this.showDisclosure.bind(this)),
            this.trigger.addEventListener("mouseleave", this.hideDisclosure.bind(this)),
            this.trigger.addEventListener("focusout", function(t) {
                this.trigger.contains(t.relatedTarget) || this.hideDisclosure()
            }
            .bind(this)),
            this.disclosure.addEventListener("keyup", function(t) {
                t.which === window.theme.keyboardKeys.ESCAPE && this.hideDisclosure()
            }
            .bind(this))
        }
    }
    const ci = {
        onLoad() {
            ri[this.id] = [],
            ai = this.container.querySelectorAll(Qe),
            ai.forEach((t=>{
                ri[this.id].push(new li(t))
            }
            ))
        },
        onBlockSelect(t) {
            ri[this.id].forEach((e=>{
                "function" == typeof e.onBlockSelect && e.onBlockSelect(t)
            }
            ))
        },
        onBlockDeselect(t) {
            ri[this.id].forEach((e=>{
                "function" == typeof e.onBlockDeselect && e.onBlockDeselect(t)
            }
            ))
        },
        onUnload: function() {
            ri[this.id].forEach((t=>{
                "function" == typeof t.unload && t.unload()
            }
            ))
        }
    }
      , hi = "[data-main-menu-text-item]"
      , di = "[data-text-items-wrapper]"
      , ui = ".navtext"
      , pi = "data-menu-active"
      , mi = "[data-header-wrapper]"
      , yi = "data-underline-current"
      , fi = ".menu__item.main-menu--active .navtext, .header__desktop__button.main-menu--active .navtext";
    let gi = {}
      , wi = null;
    class vi {
        constructor(t) {
            this.wrapper = t,
            this.itemList = this.wrapper.querySelectorAll(hi),
            this.sectionOuter = document.querySelector(mi),
            this.underlineCurrent = "true" === this.sectionOuter.getAttribute(yi),
            this.defaultItem = null,
            this.underlineCurrent && (this.defaultItem = this.wrapper.querySelector(fi)),
            this.setDefault(),
            document.fonts.ready.then((()=>{
                this.init()
            }
            ))
        }
        init() {
            if (this.itemList.length) {
                if (this.listen(),
                this.listenResize(),
                this.textBottom = null,
                this.setHeight(),
                wi) {
                    if (this.defaultItem) {
                        const t = this.defaultItem.offsetLeft || 0;
                        this.sectionOuter.style.setProperty("--bar-left", t + "px")
                    }
                    this.reset()
                } else {
                    const t = this.sectionOuter.querySelector(hi).offsetLeft;
                    this.sectionOuter.style.setProperty("--bar-left", t + "px"),
                    this.sectionOuter.style.setProperty("--bar-width", "0px")
                }
                this.sectionOuter.style.setProperty("--bar-opacity", "1")
            }
        }
        unload() {
            document.removeEventListener("theme:resize", this.reset),
            wi = null
        }
        listenResize() {
            document.addEventListener("theme:resize", this.reset.bind(this))
        }
        setDefault() {
            this.defaultItem && (wi = {
                left: this.defaultItem.offsetLeft || null,
                width: this.defaultItem.clientWidth || null
            })
        }
        setHeight() {
            const t = this.wrapper.clientHeight
              , e = this.itemList[0].querySelector(ui).clientHeight
              , i = Math.floor(t / 2 - e / 2) - 4;
            this.textBottom !== i && (this.sectionOuter.style.setProperty("--bar-text", e + "px"),
            this.sectionOuter.style.setProperty("--bar-bottom", i + "px"),
            this.textBottom = i)
        }
        listen() {
            this.itemList.forEach((t=>{
                t.addEventListener("mouseenter", (t=>{
                    const e = t.target.querySelector(ui);
                    this.startBar(e)
                }
                ))
            }
            )),
            this.wrapper.addEventListener("mouseleave", this.clearBar.bind(this))
        }
        startBar(t) {
            this.setHeight();
            let e = "false" !== this.sectionOuter.getAttribute(pi)
              , i = t.offsetLeft
              , s = t.clientWidth;
            e ? this.render(s, i) : (this.sectionOuter.setAttribute(pi, !0),
            this.render(0, i),
            setTimeout((()=>{
                this.render(s, i)
            }
            ), 10))
        }
        render(t, e) {
            this.sectionOuter.style.setProperty("--bar-left", e + "px"),
            this.sectionOuter.style.setProperty("--bar-width", t + "px")
        }
        reset() {
            this.setDefault(),
            wi && wi.left && wi.width ? (this.sectionOuter.style.setProperty("--bar-left", wi.left + "px"),
            this.sectionOuter.style.setProperty("--bar-width", wi.width + "px")) : this.sectionOuter.style.setProperty("--bar-width", "0px")
        }
        clearBar() {
            this.sectionOuter.setAttribute(pi, !1),
            setTimeout((()=>{
                "false" !== this.sectionOuter.getAttribute(pi) || this.reset()
            }
            ), 150)
        }
    }
    const bi = {
        onLoad() {
            gi[this.id] = [];
            this.container.querySelectorAll(di).forEach((t=>{
                gi[this.id].push(new vi(t))
            }
            ))
        },
        onUnload: function() {
            gi[this.id].forEach((t=>{
                "function" == typeof t.unload && t.unload()
            }
            )),
            delete gi[this.id]
        }
    }
      , Si = "data-header-cart-price"
      , Ei = "data-header-cart-count"
      , Li = "data-header-cart-full";
    class Ti {
        constructor(t) {
            this.section = t,
            this.counts = this.section.querySelectorAll(`[${Ei}]`),
            this.prices = this.section.querySelectorAll(`[${Si}]`),
            this.dots = this.section.querySelectorAll(`[${Li}]`),
            this.cart = null,
            this.listen()
        }
        listen() {
            document.addEventListener("theme:cart:change", function(t) {
                this.cart = t.detail.cart,
                this.update()
            }
            .bind(this))
        }
        update() {
            this.cart && (this.prices.forEach((t=>{
                t.setAttribute(Si, this.cart.total_price);
                const e = n.formatMoney(this.cart.total_price, theme.moneyFormat);
                t.innerHTML = e
            }
            )),
            this.counts.forEach((t=>{
                t.setAttribute(Ei, this.cart.item_count),
                t.innerHTML = `(${this.cart.item_count})`
            }
            )),
            this.dots.forEach((t=>{
                const e = this.cart.item_count > 0;
                t.setAttribute(Li, e)
            }
            )))
        }
    }
    const ki = {
        onLoad() {
            new Ti(this.container)
        }
    }
      , Ai = "[data-search-popdown-wrap]"
      , qi = "data-popdown-toggle"
      , xi = "[data-close-popdown]"
      , _i = "[data-predictive-search-input]"
      , Pi = "[data-search-underlay]"
      , Ci = "underlay--visible"
      , Di = "is-visible";
    let Mi = {};
    class Hi {
        constructor(t) {
            this.trigger = t,
            this.key = this.trigger.getAttribute(qi);
            const e = `[id='${this.key}']`;
            this.popdown = document.querySelector(e),
            this.input = this.popdown.querySelector(_i),
            this.close = this.popdown.querySelector(xi),
            this.wrapper = this.popdown.closest(Ai),
            this.underlay = this.wrapper.querySelector(Pi),
            this.initTriggerEvents(),
            this.initPopdownEvents()
        }
        initTriggerEvents() {
            this.trigger.setAttribute("aria-haspopup", !0),
            this.trigger.setAttribute("aria-expanded", !1),
            this.trigger.setAttribute("aria-controls", this.key),
            this.trigger.addEventListener("click", function(t) {
                t.preventDefault(),
                this.showPopdown()
            }
            .bind(this)),
            this.trigger.addEventListener("keyup", function(t) {
                t.which === window.theme.keyboardKeys.SPACE && this.showPopdown()
            }
            .bind(this))
        }
        initPopdownEvents() {
            this.popdown.addEventListener("keyup", function(t) {
                t.which === window.theme.keyboardKeys.ESCAPE && this.hidePopdown()
            }
            .bind(this)),
            this.close.addEventListener("click", function() {
                this.hidePopdown()
            }
            .bind(this)),
            this.underlay.addEventListener("click", function() {
                this.hidePopdown()
            }
            .bind(this))
        }
        hidePopdown() {
            this.popdown.classList.remove(Di),
            this.underlay.classList.remove(Ci),
            this.trigger.focus(),
            this.input.value = "",
            jt(),
            this.input.dispatchEvent(new CustomEvent("clear",{
                bubbles: !1
            })),
            this.popdown.dispatchEvent(new CustomEvent("theme:scroll:unlock",{
                bubbles: !0
            }))
        }
        showPopdown() {
            this.input.value = "",
            this.popdown.classList.add(Di),
            this.underlay.classList.add(Ci),
            Wt(this.popdown, {
                elementToFocus: this.input
            }),
            this.popdown.dispatchEvent(new CustomEvent("theme:scroll:lock",{
                bubbles: !0
            }))
        }
    }
    const Ii = {
        onLoad() {
            Mi[this.id] = {};
            const t = this.container.querySelector(`[${qi}]`);
            t && (Mi[this.id] = new Hi(t))
        },
        onUnload: function() {
            "function" == typeof Mi[this.id].unload && Mi[this.id].unload()
        }
    };
    function Bi(t, e) {
        if (null === e)
            return t;
        if (null == t && (t = window.theme.assets.noImage),
        "master" === e)
            return $i(t);
        const i = t.match(/\.(jpg|jpeg|gif|png|bmp|bitmap|tiff|tif)(\?v=\d+)?$/i);
        if (i) {
            const s = t.split(i[0])
              , n = i[0];
            return $i(`${s[0]}_${e}${n}`)
        }
        return null
    }
    function $i(t) {
        return t.replace(/http(s)?:/, "")
    }
    function Fi() {
        this.entries = []
    }
    function Oi(t, e) {
        return Wi(t),
        function(t, e) {
            return Wi(t),
            function(t) {
                if (Array.isArray(t) && "object" == typeof t[0])
                    throw new Error(t + "is not a valid array of options.")
            }(e),
            t.variants.filter((function(t) {
                return e.every((function(e, i) {
                    return t.options[i] === e
                }
                ))
            }
            ))[0] || null
        }(t, function(t, e) {
            Wi(t),
            function(t) {
                if (!Array.isArray(t))
                    throw new TypeError(t + " is not an array.");
                if (0 === t.length)
                    throw new Error(t + " is empty.");
                if (!t[0].hasOwnProperty("name"))
                    throw new Error(t[0] + "does not contain name key.");
                if ("string" != typeof t[0].name)
                    throw new TypeError("Invalid value type passed for name of option " + t[0].name + ". Value should be string.")
            }(e);
            var i = [];
            return e.forEach((function(e) {
                for (var s = 0; s < t.options.length; s++) {
                    if ((t.options[s].name || t.options[s]).toLowerCase() === e.name.toLowerCase()) {
                        i[s] = e.value;
                        break
                    }
                }
            }
            )),
            i
        }(t, e))
    }
    function Wi(t) {
        if ("object" != typeof t)
            throw new TypeError(t + " is not an object.");
        if (0 === Object.keys(t).length && t.constructor === Object)
            throw new Error(t + " is empty.")
    }
    Fi.prototype.add = function(t, e, i) {
        this.entries.push({
            element: t,
            event: e,
            fn: i
        }),
        t.addEventListener(e, i)
    }
    ,
    Fi.prototype.removeAll = function() {
        this.entries = this.entries.filter((function(t) {
            return t.element.removeEventListener(t.event, t.fn),
            !1
        }
        ))
    }
    ;
    var ji = '[name="id"]'
      , Ni = '[name="selling_plan"]'
      , zi = '[name^="options"]'
      , Vi = '[name="quantity"]'
      , Ri = '[name^="properties"]';
    class Ui {
        constructor(t, e, i) {
            this.element = t,
            this.form = "FORM" == this.element.tagName ? this.element : this.element.querySelector("form"),
            this.product = this._validateProductObject(e),
            this.variantElement = this.element.querySelector(ji),
            i = i || {},
            this._listeners = new Fi,
            this._listeners.add(this.element, "submit", this._onSubmit.bind(this, i)),
            this.optionInputs = this._initInputs(zi, i.onOptionChange),
            this.planInputs = this._initInputs(Ni, i.onPlanChange),
            this.quantityInputs = this._initInputs(Vi, i.onQuantityChange),
            this.propertyInputs = this._initInputs(Ri, i.onPropertyChange)
        }
        destroy() {
            this._listeners.removeAll()
        }
        options() {
            return this._serializeInputValues(this.optionInputs, (function(t) {
                return t.name = /(?:^(options\[))(.*?)(?:\])/.exec(t.name)[2],
                t
            }
            ))
        }
        variant() {
            const t = this.options();
            return t.length ? Oi(this.product, t) : this.product.variants[0]
        }
        plan(t) {
            let e = {
                allocation: null,
                group: null,
                detail: null
            };
            const i = new FormData(this.form).get("selling_plan");
            return i && t && (e.allocation = t.selling_plan_allocations.find((function(t) {
                return t.selling_plan_id.toString() === i.toString()
            }
            ))),
            e.allocation && (e.group = this.product.selling_plan_groups.find((function(t) {
                return t.id.toString() === e.allocation.selling_plan_group_id.toString()
            }
            ))),
            e.group && (e.detail = e.group.selling_plans.find((function(t) {
                return t.id.toString() === i.toString()
            }
            ))),
            e && e.allocation && e.detail && e.allocation ? e : null
        }
        properties() {
            return this._serializeInputValues(this.propertyInputs, (function(t) {
                return t.name = /(?:^(properties\[))(.*?)(?:\])/.exec(t.name)[2],
                t
            }
            ))
        }
        quantity() {
            return this.quantityInputs[0] ? Number.parseInt(this.quantityInputs[0].value, 10) : 1
        }
        getFormState() {
            const t = this.variant();
            return {
                options: this.options(),
                variant: t,
                properties: this.properties(),
                quantity: this.quantity(),
                plan: this.plan(t)
            }
        }
        _setIdInputValue(t) {
            t && t.id ? this.variantElement.value = t.id.toString() : this.variantElement.value = "",
            this.variantElement.dispatchEvent(new Event("change"))
        }
        _onSubmit(t, e) {
            e.dataset = this.getFormState(),
            t.onFormSubmit && t.onFormSubmit(e)
        }
        _onOptionChange(t) {
            this._setIdInputValue(t.dataset.variant)
        }
        _onFormEvent(t) {
            return void 0 === t ? Function.prototype : function(e) {
                e.dataset = this.getFormState(),
                this._setIdInputValue(e.dataset.variant),
                t(e)
            }
            .bind(this)
        }
        _initInputs(t, e) {
            return Array.prototype.slice.call(this.element.querySelectorAll(t)).map(function(t) {
                return this._listeners.add(t, "change", this._onFormEvent(e)),
                t
            }
            .bind(this))
        }
        _serializeInputValues(t, e) {
            return t.reduce((function(t, i) {
                return (i.checked || "radio" !== i.type && "checkbox" !== i.type) && t.push(e({
                    name: i.name,
                    value: i.value
                })),
                t
            }
            ), [])
        }
        _validateProductObject(t) {
            if ("object" != typeof t)
                throw new TypeError(t + " is not an object.");
            if (void 0 === t.variants[0].options)
                throw new TypeError("Product object is invalid. Make sure you use the product object that is output from {{ product | json }} or from the http://[your-product-url].js route");
            return t
        }
    }
    const Ji = {};
    function Ki(t={}) {
        if (t.type || (t.type = "json"),
        t.url)
            return Ji[t.url] ? Ji[t.url] : function(t, e) {
                const i = new Promise(((i,s)=>{
                    "text" === e ? fetch(t).then((t=>t.text())).then((t=>{
                        i(t)
                    }
                    )).catch((t=>{
                        s(t)
                    }
                    )) : function(t, e, i) {
                        let s = document.getElementsByTagName("head")[0]
                          , n = !1
                          , o = document.createElement("script");
                        o.src = t,
                        o.onload = o.onreadystatechange = function() {
                            n || this.readyState && "loaded" != this.readyState && "complete" != this.readyState ? i() : (n = !0,
                            e())
                        }
                        ,
                        s.appendChild(o)
                    }(t, (function() {
                        i()
                    }
                    ), (function() {
                        s()
                    }
                    ))
                }
                ));
                return Ji[t] = i,
                i
            }(t.url, t.type);
        if (t.json)
            return Ji[t.json] ? Promise.resolve(Ji[t.json]) : window.fetch(t.json).then((t=>t.json())).then((e=>(Ji[t.json] = e,
            e)));
        if (t.name) {
            const e = "".concat(t.name, t.version);
            return Ji[e] ? Ji[e] : function(t) {
                const e = "".concat(t.name, t.version)
                  , i = new Promise(((e,i)=>{
                    try {
                        window.Shopify.loadFeatures([{
                            name: t.name,
                            version: t.version,
                            onLoad: t=>{
                                !function(t, e, i) {
                                    i ? e(i) : t()
                                }(e, i, t)
                            }
                        }])
                    } catch (t) {
                        i(t)
                    }
                }
                ));
                return Ji[e] = i,
                i
            }(t)
        }
        return Promise.reject()
    }
    const Xi = {
        color: "ash"
    }
      , Yi = "data-swatch"
      , Qi = "[data-grid-item]"
      , Gi = "[data-grid-slide]"
      , Zi = "data-swatch-image"
      , ts = "data-swatch-variant"
      , es = "[data-swatch-button]"
      , is = "[data-grid-link]"
      , ss = "[data-grid-swatches]"
      , ns = "[data-swatch-template]"
      , os = "data-swatch-handle"
      , rs = "data-swatch-label";
    class as {
        constructor(t={}) {
            this.settings = {
                ...Xi,
                ...t
            },
            this.match = this.init()
        }
        getColor() {
            return this.match
        }
        init() {
            return Ki({
                json: window.theme.assets.swatches
            }).then((t=>this.matchColors(t, this.settings.color))).catch((t=>{
                console.log("failed to load swatch colors script"),
                console.log(t)
            }
            ))
        }
        matchColors(t, e) {
            let i = "#E5E5E5"
              , s = null;
            const n = window.theme.assets.base || "/"
              , o = e.toLowerCase().replace(/\s/g, "")
              , r = t.colors;
            if (r) {
                const t = t=>Object.keys(t).toString().toLowerCase().replace(/\s/g, "") === o
                  , e = r.findIndex(t);
                if (e > -1) {
                    const t = Object.values(r[e])[0];
                    t.includes(".jpg") || t.includes(".jpeg") || t.includes(".png") || t.includes(".svg") ? (s = `${n}${t}`,
                    i = "#888888") : i = t
                }
            }
            return {
                color: this.settings.color,
                path: s,
                hex: i
            }
        }
    }
    class ls {
        constructor(t) {
            this.element = t,
            this.outer = this.element.closest(Qi),
            this.colorString = t.getAttribute(Yi),
            this.image = t.getAttribute(Zi),
            this.variant = t.getAttribute(ts);
            new as({
                color: this.colorString
            }).getColor().then((t=>{
                this.colorMatch = t,
                this.init()
            }
            ))
        }
        init() {
            this.setStyles(),
            this.variant && this.outer && this.handleClicks()
        }
        setStyles() {
            this.colorMatch.hex && this.element.style.setProperty("--swatch", "" + this.colorMatch.hex),
            this.colorMatch.path && (this.element.style.setProperty("background-image", `url(${this.colorMatch.path})`),
            this.element.style.setProperty("background-size", "cover"))
        }
        handleClicks() {
            var t, e;
            this.slide = this.outer.querySelector(Gi),
            this.linkElement = this.outer.querySelector(is),
            this.linkDestination = (t = this.linkElement.getAttribute("href"),
            e = this.variant,
            /variant=/.test(t) ? t.replace(/(variant=)[^&]+/, "$1" + e) : /\?/.test(t) ? t.concat("&variant=").concat(e) : t.concat("?variant=").concat(e)),
            this.button = this.element.closest(es),
            this.button.addEventListener("click", function() {
                if (this.linkElement.setAttribute("href", this.linkDestination),
                this.slide.setAttribute("src", this.linkDestination),
                this.image) {
                    let t = window.devicePixelRatio || 1
                      , e = this.slide.offsetWidth * t
                      , i = 180 * Math.ceil(e / 180)
                      , s = Bi(this.image, i + "x");
                    window.fetch(s).then((t=>t.blob())).then((t=>{
                        var e = URL.createObjectURL(t);
                        this.slide.style.setProperty("background-color", "#fff"),
                        this.slide.style.setProperty("background-image", `url("${e}")`)
                    }
                    )).catch((t=>{
                        console.log("Error: " + t)
                    }
                    ))
                }
            }
            .bind(this))
        }
    }
    class cs {
        constructor(t) {
            this.template = document.querySelector(ns).innerHTML,
            this.wrap = t,
            this.handle = t.getAttribute(os);
            const e = t.getAttribute(rs).trim().toLowerCase();
            (function(t) {
                const e = `${window.theme.routes.root_url}products/${t}.js`;
                return window.fetch(e).then((t=>t.json())).catch((t=>{
                    console.error(t)
                }
                ))
            }
            )(this.handle).then((t=>{
                this.product = t,
                this.colorOption = t.options.find((function(t) {
                    return t.name.toLowerCase() === e || null
                }
                )),
                this.colorOption && (this.swatches = this.colorOption.values,
                this.init())
            }
            ))
        }
        init() {
            this.wrap.innerHTML = "",
            this.swatches.forEach((t=>{
                let e = this.product.variants.find((e=>e.options.includes(t)));
                const i = e.featured_media ? e.featured_media.preview_image.src : ""
                  , s = Math.floor(9999 * Math.random());
                this.wrap.innerHTML += m.render(this.template, {
                    color: t,
                    uniq: `${this.product.id}-${e.id}-${s}`,
                    variant: e.id,
                    image: i
                })
            }
            )),
            this.swatchElements = this.wrap.querySelectorAll(`[${Yi}]`),
            this.swatchElements.forEach((t=>{
                new ls(t)
            }
            ))
        }
    }
    function hs(t) {
        t.querySelectorAll(ss).forEach((t=>{
            new cs(t)
        }
        ))
    }
    const ds = {
        onLoad() {
            this.swatches = [];
            this.container.querySelectorAll(`[${Yi}]`).forEach((t=>{
                this.swatches.push(new ls(t))
            }
            ))
        }
    }
      , us = {
        onLoad() {
            hs(this.container)
        }
    }
      , ps = (t,e=500,i=!0)=>{
        let s = window.getComputedStyle(t).display;
        if (i && "none" !== s)
            return;
        t.style.removeProperty("display"),
        "none" === s && (s = "block"),
        t.style.display = s;
        let n = t.offsetHeight;
        t.style.overflow = "hidden",
        t.style.height = 0,
        t.style.paddingTop = 0,
        t.style.paddingBottom = 0,
        t.style.marginTop = 0,
        t.style.marginBottom = 0,
        t.offsetHeight,
        t.style.boxSizing = "border-box",
        t.style.transitionTimingFunction = "cubic-bezier(0.215, 0.61, 0.355, 1)",
        t.style.transitionProperty = "height, margin, padding",
        t.style.transitionDuration = e + "ms",
        t.style.height = n + "px",
        t.style.removeProperty("padding-top"),
        t.style.removeProperty("padding-bottom"),
        t.style.removeProperty("margin-top"),
        t.style.removeProperty("margin-bottom"),
        window.setTimeout((()=>{
            t.style.removeProperty("height"),
            t.style.removeProperty("overflow"),
            t.style.removeProperty("transition-duration"),
            t.style.removeProperty("transition-property"),
            t.style.removeProperty("transition-timing-function")
        }
        ), e)
    }
      , ms = (t,e=500)=>{
        t.style.transitionProperty = "height, margin, padding",
        t.style.transitionTimingFunction = "cubic-bezier(0.215, 0.61, 0.355, 1)",
        t.style.transitionDuration = e + "ms",
        t.style.boxSizing = "border-box",
        t.style.height = t.offsetHeight + "px",
        t.offsetHeight,
        t.style.overflow = "hidden",
        t.style.height = 0,
        t.style.paddingTop = 0,
        t.style.paddingBottom = 0,
        t.style.marginTop = 0,
        t.style.marginBottom = 0,
        window.setTimeout((()=>{
            t.style.display = "none",
            t.style.removeProperty("height"),
            t.style.removeProperty("padding-top"),
            t.style.removeProperty("padding-bottom"),
            t.style.removeProperty("margin-top"),
            t.style.removeProperty("margin-bottom"),
            t.style.removeProperty("overflow"),
            t.style.removeProperty("transition-duration"),
            t.style.removeProperty("transition-property"),
            t.style.removeProperty("transition-timing-function")
        }
        ), e)
    }
    ;
    class ys {
        constructor(t) {
            this.inputs = t.querySelectorAll("[data-cart-note]"),
            this.initInputs()
        }
        initInputs() {
            this.inputs.forEach((t=>{
                t.addEventListener("change", function(t) {
                    const e = t.target.value.toString() || "";
                    this.saveNotes(e)
                }
                .bind(this))
            }
            ))
        }
        saveNotes(t) {
            window.fetch(window.theme.routes.cart + "/update.js", {
                method: "post",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    note: t
                })
            }).catch((t=>{
                console.error(t)
            }
            ))
        }
    }
    const fs = (t,e=[],i=!1)=>{
        const s = Object.keys(t).map((s=>{
            let n = t[s];
            if ("[object Object]" === Object.prototype.toString.call(n) || Array.isArray(n))
                return Array.isArray(t) ? e.push("") : e.push(s),
                fs(n, e, Array.isArray(n));
            {
                let t = s;
                if (e.length > 0) {
                    t = (i ? e : [...e, s]).reduce(((t,e)=>"" === t ? e : `${t}[${e}]`), "")
                }
                return i ? `${t}[]=${n}` : `${t}=${n}`
            }
        }
        )).join("&");
        return e.pop(),
        s
    }
      , gs = "[data-submit-shipping]"
      , ws = "[data-shipping-estimate-form]"
      , vs = "[data-response-template]"
      , bs = "#estimate_address_country"
      , Ss = "#estimate_address_province"
      , Es = "#estimate_address_zip"
      , Ls = "[data-response-wrapper]"
      , Ts = "data-default-fullname"
      , ks = "shipping--success"
      , As = "errors";
    class qs {
        constructor(t) {
            this.button = t.container.querySelector(gs),
            this.template = t.container.querySelector(vs).innerHTML,
            this.ratesWrapper = t.container.querySelector(Ls),
            this.form = t.container.querySelector(ws),
            this.country = t.container.querySelector(bs),
            this.province = t.container.querySelector(Ss),
            this.zip = t.container.querySelector(Es),
            this.init()
        }
        enableButtons() {
            this.button.removeAttribute("disabled"),
            this.button.classList.remove("disabled")
        }
        disableButtons() {
            this.button.setAttribute("disabled", "disabled"),
            this.button.classList.add("disabled")
        }
        render(t) {
            if (this.template && this.ratesWrapper) {
                const e = m.render(this.template, t);
                this.ratesWrapper.innerHTML = e
            }
            this.enableButtons(),
            this.ratesWrapper.style.removeProperty("display")
        }
        estimate(t) {
            const e = encodeURI(fs({
                shipping_address: t
            }))
              , i = `${window.theme.routes.cart}/shipping_rates.json?${e}`
              , s = this;
            a.get(i).then((function(t) {
                const e = s.sanitize(t);
                s.render(e),
                s.enableButtons(),
                s.ratesWrapper.style.removeProperty("display")
            }
            )).catch((function(t) {
                const e = s.sanitizeErrors(t);
                s.render(e)
            }
            ))
        }
        sanitize(t) {
            const e = {};
            if (e.class = ks,
            e.items = [],
            t.data.shipping_rates && t.data.shipping_rates.length > 0) {
                t.data.shipping_rates.forEach((t=>{
                    let i = {};
                    i.title = t.presentment_name,
                    i.value = n.formatMoney(t.price, theme.moneyFormat),
                    e.items.push(i)
                }
                ))
            } else
                e.items[0] = {
                    value: theme.strings.noShippingAvailable
                };
            return e
        }
        sanitizeErrors(t) {
            const e = {};
            if (e.class = As,
            e.items = [],
            "object" == typeof t.data)
                for (const [i,s] of Object.entries(t.data)) {
                    let t = {};
                    t.title = i.toString(),
                    t.value = s.toString(),
                    e.items.push(t)
                }
            else
                e.items[0] = {
                    value: theme.strings.noShippingAvailable
                };
            return e
        }
        init() {
            const t = document.querySelector("html");
            let e = "en";
            t.hasAttribute("lang") && "" !== t.getAttribute("lang") && (e = t.getAttribute("lang")),
            this.form && r.AddressForm(this.form, e, {
                shippingCountriesOnly: !0
            }),
            this.country && this.country.hasAttribute("data-default") && this.province && this.province.hasAttribute("data-default") && this.country.addEventListener("change", (function() {
                this.country.removeAttribute("data-default"),
                this.province.removeAttribute("data-default")
            }
            )),
            this.button && this.button.addEventListener("click", function(t) {
                for (t.preventDefault(),
                this.disableButtons(); this.ratesWrapper.firstChild; )
                    this.ratesWrapper.removeChild(this.ratesWrapper.firstChild);
                this.ratesWrapper.style.display = "none";
                const e = {};
                let i = this.country.value
                  , s = this.province.value;
                const n = this.country.getAttribute(Ts);
                "" === i && n && "" !== n && (i = n);
                const o = this.province.getAttribute(Ts);
                "" === s && o && "" !== o && (s = o),
                e.zip = this.zip.value || "",
                e.country = i || "",
                e.province = s || "",
                this.estimate(e)
            }
            .bind(this))
        }
    }
    let xs = {};
    const _s = "[data-add-action-wrapper]"
      , Ps = "[data-add-to-cart]"
      , Cs = "[data-add-action-errors]"
      , Ds = "data-add-to-cart-variant"
      , Ms = "[data-product-add-popdown-wrapper]"
      , Hs = "loading"
      , Is = "has-success";
    class Bs {
        constructor(t, e) {
            if (this.wrapper = t,
            this.isCartItem = e || !1,
            this.button = t.querySelector(Ps),
            this.errors = t.querySelector(Cs),
            this.popdown = document.querySelector(Ms),
            this.button) {
                this.button.hasAttribute(Ds) ? this.initDetached() : this.initWithForm()
            }
        }
        initWithForm() {
            this.button.addEventListener("click", function(t) {
                const e = t.target.closest("form");
                if (e.querySelector('[type="file"]'))
                    return;
                t.preventDefault(),
                this.button.setAttribute("disabled", !0),
                this.button.classList.add(Hs);
                const i = new FormData(e)
                  , s = new URLSearchParams(i).toString();
                this.addToCartAction(s)
            }
            .bind(this))
        }
        initDetached() {
            this.button.addEventListener("click", function(t) {
                t.preventDefault(),
                this.button.setAttribute("disabled", !0),
                this.button.classList.add(Hs);
                const e = "form_type=product&id=" + this.button.getAttribute(Ds);
                this.addToCartAction(e)
            }
            .bind(this))
        }
        addToCartAction(t) {
            const e = window.theme.routes.cart + "/add.js"
              , i = this;
            a.post(e, t, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            }).then((function(t) {
              Shopify.getCart(function(cart){
                i.onSuccess(t.data)
              }.bind(this));
            }
            )).catch((function(t) {
                console.warn(t),
                i.onError(t.data)
            }
            ))
        }
        onSuccess(t) {
            this.updateHeaderTotal(),
            this.button.classList.remove(Hs),
            this.button.classList.add(Is),
            setTimeout((()=>{
                this.button.classList.remove(Is),
                this.button.removeAttribute("disabled")
            }
            ), 3500),
            this.isCartItem ? document.dispatchEvent(new CustomEvent("theme:cart:reload",{
                bubbles: !0
            })) : this.popdown.dispatchEvent(new CustomEvent("theme:cart:popdown",{
                detail: {
                    variant: t
                },
                bubbles: !0
            }))
        }
        onError(t) {
            let e = "Network error: please try again";
            t && t.description && (e = t.description);
            const i = `<div class="errors">${e}</div>`;
            this.button.classList.remove(Hs),
            this.button.removeAttribute("disabled"),
            this.errors.innerHTML = i,
            ps(this.errors),
            setTimeout((()=>{
                ms(this.errors)
            }
            ), 5e3)
        }
        updateHeaderTotal() {
            a.get(window.theme.routes.cart + ".js").then((t=>{
                document.dispatchEvent(new CustomEvent("theme:cart:change",{
                    detail: {
                        cart: t.data
                    },
                    bubbles: !0
                }))
            }
            )).catch((t=>{
                console.error(t)
            }
            ))
        }
    }
    const $s = {
        onLoad() {
            xs[this.id] = [];
            this.container.querySelectorAll(_s).forEach((t=>{
                xs[this.id].push(new Bs(t))
            }
            ))
        },
        onUnload: function() {
            xs[this.id].forEach((t=>{
                "function" == typeof t.unload && t.unload()
            }
            ))
        }
    }
      , Fs = "[data-quantity-selector]"
      , Os = "[data-increase-quantity]"
      , Ws = "[data-decrease-quantity]"
      , js = "[data-quantity-input]";
    class Ns {
        constructor(t) {
            this.wrapper = t,
            this.increase = this.wrapper.querySelector(Os),
            this.decrease = this.wrapper.querySelector(Ws),
            this.input = this.wrapper.querySelector(js),
            this.min = parseInt(this.input.getAttribute("min"), 10),
            this.initButtons()
        }
        initButtons() {
            this.increase.addEventListener("click", function(t) {
                t.preventDefault();
                let e = parseInt(this.input.value, 10);
                e = isNaN(e) ? 0 : e,
                e++,
                this.input.value = e,
                this.input.dispatchEvent(new Event("change"))
            }
            .bind(this)),
            this.decrease.addEventListener("click", function(t) {
                t.preventDefault();
                let e = parseInt(this.input.value, 10);
                e = isNaN(e) ? 0 : e,
                e--,
                e = Math.max(this.min, e),
                this.input.value = e,
                this.input.dispatchEvent(new Event("change"))
            }
            .bind(this))
        }
    }
    function zs(t) {
        t.querySelectorAll(Fs).forEach((t=>{
            new Ns(t)
        }
        ))
    }
    const Vs = '[data-drawer="drawer-cart"]'
      , Rs = "[data-shipping-estimate-form]"
      , Us = "[data-cart-loading]"
      , Js = "[data-cart-form]"
      , Ks = "[data-cart-empty]"
      , Xs = "[data-line-items]"
      , Ys = "[data-cart-subtotal]"
      , Qs = "[data-cart-bottom]"
      , Gs = "[data-form-errors]"
      , Zs = "[data-cart-item]"
      , tn = "[data-cart-final]"
      , en = "data-update-cart"
      , sn = "data-remove-key"
      , nn = "[data-upsell-holder]"
      , on = '[data-section-type="cart"]'
      , rn = "cart--hidden"
      , an = "cart--loading";
    class ln {
        constructor(t) {
            this.container = t.container,
            this.drawer = this.container.querySelector(Vs),
            this.form = this.container.querySelector(Js),
            this.loader = this.container.querySelector(Us),
            this.bottom = this.container.querySelector(Qs),
            this.items = this.container.querySelector(Xs),
            this.subtotal = this.container.querySelector(Ys),
            this.errors = this.container.querySelector(Gs),
            this.finalPrice = this.container.querySelector(tn),
            this.emptystate = this.container.querySelector(Ks),
            this.latestClick = null,
            this.cart = null,
            this.stale = !0,
            this.cartPage = document.querySelector(on),
            this.listen()
        }
        listen() {
            document.addEventListener("theme:cart:change", function(t) {
                this.cart = t.detail.cart,
                this.stale = !0
            }
            .bind(this)),
            document.addEventListener("theme:cart:init", function() {
                this.init()
            }
            .bind(this)),
            document.addEventListener("theme:cart:reload", function() {
                this.stale = !0,
                this.cart ? this.loadHTML() : this.init().then((()=>this.loadHTML()))
            }
            .bind(this)),
            this.drawer && this.drawer.addEventListener("theme:drawer:open", function() {
                this.cart ? this.loadHTML() : this.init().then((()=>this.loadHTML()))
            }
            .bind(this)),
            new ys(this.container),
            new ye(this.container)
        }
        init() {
            return window.fetch(window.theme.routes.cart + ".js").then(this.handleErrors).then((t=>t.json())).then((t=>(this.cart = t,
            this.fireChange(t),
            t))).catch((t=>{
                console.error(t)
            }
            ))
        }
        loadHTML() {
            this.stale && (this.cart && this.cart.item_count > 0 ? this.loadForm() : this.showEmpty()),
            this.stale = !1
        }
        initInputs() {
            this.inputs = this.container.querySelectorAll(`[${en}]`),
            this.inputs.forEach((t=>{
                const e = t.getAttribute(en);
                t.addEventListener("change", function(t) {
                    const i = parseInt(t.target.value, 10);
                    this.latestClick = t.target.closest(Zs),
                    this.lockState(),
                    this.updateCart(e, i)
                }
                .bind(this))
            }
            ))
        }
        initRemove() {
            this.removers = this.container.querySelectorAll(`[${sn}]`),
            this.removers.forEach((t=>{
                const e = t.getAttribute(sn);
                t.addEventListener("click", function(t) {
                    t.preventDefault(),
                    this.latestClick = t.target.closest(Zs),
                    this.lockState(),
                    this.updateCart(e, 0)
                }
                .bind(this))
            }
            ))
        }
        lockState() {
            this.latestClick.querySelector(".item--loadbar").style.display = "block",
            this.loader.classList.add(an)
        }
        updateCart(t, e) {
            let i = null
              , s = null
              , n = null;
            window.fetch(window.theme.routes.cart + ".js").then(this.handleErrors).then((t=>t.json())).then((s=>{
                const o = s.items.findIndex((e=>e.key === t));
                i = s.item_count,
                n = s.items[o].title;
                const r = {
                    line: "" + (o + 1),
                    quantity: e
                };
                return window.fetch(window.theme.routes.cart + "/change.js", {
                    method: "post",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(r)
                })
            }
            )).then(this.handleErrors).then((t=>t.json())).then((t=>{
              Shopify.getCart(function(t){
                this.cart = t,
                s = t.item_count,
                i === s ? (this.stockoutError(n),
                this.stale = !0) : (ms(this.errors),
                this.fireChange(t),
                this.stale = !0),
                this.loadHTML()
              }.bind(this));
            }
            )).catch((t=>{
                console.error(t);
                let e = "";
                void 0 !== t.status && (e = `<p>${t.status}</p>`);
                let i = t.json.description || "";
                this.showError("" + (e + i)),
                this.loadHTML()
            }
            ))
        }
        fireChange(t) {
            document.dispatchEvent(new CustomEvent("theme:cart:change",{
                detail: {
                    cart: t
                },
                bubbles: !0
            }))
        }
        updateTotal() {
            if (this.cart && this.cart.total_price) {
                const t = n.formatMoney(this.cart.total_price, theme.moneyFormat);
                this.finalPrice.innerHTML = t
            }
            this.subtotal && this.cart && window.fetch(window.theme.routes.root_url + "?section_id=api-cart-subtotal").then(this.handleErrors).then((t=>t.text())).then((t=>{
                const e = document.createElement("div");
                e.innerHTML = t,
                this.subtotal.innerHTML = e.querySelector("[data-api-content]").innerHTML
            }
            ))
        }
        showError(t) {
            ms(this.errors),
            this.errors.innerHTML = t,
            window.setTimeout((()=>{
                ps(this.errors)
            }
            ), 600)
        }
        stockoutError(t) {
            let e = `<p><strong>${window.theme.strings.stockout}</strong></p>`
              , i = `<p>${t}</p>`;
            this.showError("" + (e + i))
        }
        loadForm() {
            window.fetch(window.theme.routes.root_url + "?section_id=api-cart-items").then(this.handleErrors).then((t=>t.text())).then((t=>{
                const e = document.createElement("div");
                e.innerHTML = t,
                this.items.innerHTML = e.querySelector("[data-api-content]").innerHTML,
                this.showForm(),
                this.initQuantity(),
                this.initUpsell(),
                this.updateTotal()
            }
            ))
        }
        initUpsell() {
            const t = this.items.querySelector(nn)
              , e = this.bottom.querySelector(nn)
              , i = this.items.querySelector("[data-add-action-wrapper]");
            if (e && e.remove(),
            this.cartPage && t && this.bottom.insertBefore(t, this.bottom.firstChild),
            t && i) {
                new Bs(i,!0)
            }
        }
        initQuantity() {
            zs(this.container),
            this.initInputs(),
            this.initRemove()
        }
        showForm() {
            this.form.classList.remove(rn),
            this.bottom.classList.remove(rn),
            this.loader.classList.remove(an),
            this.emptystate.classList.add(rn)
        }
        showEmpty() {
            this.emptystate.classList.remove(rn),
            this.loader.classList.remove(an),
            this.form.classList.add(rn),
            this.bottom.classList.add(rn)
        }
        handleErrors(t) {
            return t.ok ? t : t.json().then((function(e) {
                throw new O({
                    status: t.statusText,
                    headers: t.headers,
                    json: e
                })
            }
            ))
        }
    }
    const cn = {
        onLoad() {
            this.container.querySelector(Vs) && (this.cart = new ln(this));
            this.container.querySelector(Rs) && new qs(this)
        },
        onUnload: function() {
            this.cart && "function" == typeof this.cart.unload && this.cart.unload()
        }
    }
      , hn = "[data-accordion-group]"
      , dn = "data-accordion-trigger"
      , un = "[data-accordion-body]"
      , pn = "data-accordion-body-mobile"
      , mn = "data-range-holder"
      , yn = "[data-section-id]"
      , fn = "accordion-is-open";
    let gn = {};
    class wn {
        constructor(t) {
            this.body = t,
            this.key = this.body.id;
            const e = `[${dn}='${this.key}']`;
            this.trigger = document.querySelector(e),
            this.toggleEvent = t=>this.clickEvents(t),
            this.keyboardEvent = t=>this.keyboardEvents(t),
            this.hideEvent = ()=>this.hideEvents(),
            this.syncBodies = this.getSiblings(),
            this.body.hasAttribute(pn) ? this.mobileAccordions() : this.init()
        }
        mobileAccordions() {
            window.innerWidth < window.theme.sizes.medium ? (this.init(),
            this.setDefaultState()) : (this.resetMobileAccordions(),
            this.body.removeAttribute("style")),
            document.addEventListener("theme:resize", (()=>{
                window.innerWidth < window.theme.sizes.medium ? (this.init(),
                this.setDefaultState()) : (this.resetMobileAccordions(),
                this.body.removeAttribute("style"))
            }
            ))
        }
        init() {
            this.trigger.setAttribute("aria-haspopup", !0),
            this.trigger.setAttribute("aria-expanded", !1),
            this.trigger.setAttribute("aria-controls", this.key),
            this.setDefaultState(),
            this.trigger.addEventListener("click", this.toggleEvent),
            this.body.addEventListener("keyup", this.keyboardEvent),
            this.body.addEventListener("theme:accordion:close", this.hideEvent)
        }
        hideEvents() {
            this.hideAccordion()
        }
        clickEvents(t) {
            t.preventDefault(),
            this.toggleState()
        }
        keyboardEvents(t) {
            t.which === window.theme.keyboardKeys.ESCAPE && (this.hideAccordion(),
            this.trigger.focus())
        }
        resetMobileAccordions() {
            this.trigger.removeEventListener("click", this.toggleEvent),
            this.body.removeEventListener("keyup", this.keyboardEvent),
            this.body.removeEventListener("theme:accordion:close", this.hideEvent)
        }
        setDefaultState() {
            this.trigger.classList.contains(fn) ? F(this.body) : this.hideAccordion()
        }
        getSiblings() {
            const t = [...this.body.closest(yn).querySelectorAll(hn)].filter((t=>t.contains(this.body))).shift();
            if (t) {
                return [...t.querySelectorAll(un)].filter((t=>!t.contains(this.body)))
            }
            return []
        }
        closeSiblings() {
            this.syncBodies.forEach((t=>{
                t.dispatchEvent(new CustomEvent("theme:accordion:close",{
                    bubbles: !1
                }))
            }
            ))
        }
        toggleState() {
            this.trigger.classList.contains(fn) ? this.hideAccordion() : (this.showAccordion(),
            this.closeSiblings(),
            this.body.hasAttribute(mn) && setTimeout((()=>{
                document.dispatchEvent(new CustomEvent("theme:reset-price-range",{
                    bubbles: !1
                }))
            }
            ), 400))
        }
        hideAccordion() {
            this.trigger.classList.remove(fn),
            ms(this.body)
        }
        showAccordion() {
            this.trigger.classList.add(fn),
            ps(this.body)
        }
        onBlockSelect(t) {
            this.body.contains(t.target) && this.showAccordion()
        }
        onBlockDeselect(t) {
            this.body.contains(t.target) && this.hideAccordion()
        }
    }
    const vn = {
        onLoad() {
            gn[this.id] = [];
            this.container.querySelectorAll(un).forEach((t=>{
                gn[this.id].push(new wn(t))
            }
            ))
        },
        onUnload: function() {
            gn[this.id].forEach((t=>{
                "function" == typeof t.unload && t.unload()
            }
            ))
        },
        onSelect: function() {
            "accordion-single" === this.type && this.container.querySelector(`[${dn}]`).click()
        },
        onDeselect: function() {
            "accordion-single" === this.type && this.container.querySelector(`[${dn}]`).click()
        },
        onBlockSelect(t) {
            gn[this.id].forEach((e=>{
                "function" == typeof e.onBlockSelect && e.onBlockSelect(t)
            }
            ))
        },
        onBlockDeselect(t) {
            gn[this.id].forEach((e=>{
                "function" == typeof e.onBlockSelect && e.onBlockDeselect(t)
            }
            ))
        }
    }
      , bn = "on-sale"
      , Sn = "sold-out";
    const En = "[data-search-popdown-wrap]"
      , Ln = "[data-predictive-search-results]"
      , Tn = "[data-predictive-search-input]"
      , kn = "[data-search-product-template]"
      , An = "[data-search-other-template]"
      , qn = "[data-predictive-search-title-template]"
      , xn = "[data-predictive-search-aria-template]"
      , _n = "[data-product-title-wrap]"
      , Pn = "[data-product-wrap]"
      , Cn = "[data-collection-wrap]"
      , Dn = "[data-article-wrap]"
      , Mn = "[data-page-wrap]"
      , Hn = "[data-predictive-search-aria]"
      , In = "[data-popdown-outer]"
      , Bn = "[data-loading-indicator]"
      , $n = "dirty"
      , Fn = "search--empty";
    let On = {};
    m.filters.define("animationDelay", (function(t) {
        return 90 * t + 10
    }
    ));
    class Wn {
        constructor(t) {
            this.wrapper = t,
            this.input = this.wrapper.querySelector(Tn),
            this.loader = this.wrapper.querySelector(Bn),
            this.results = this.wrapper.querySelector(Ln),
            this.outer = this.input.closest(In),
            this.productTemplate = this.wrapper.querySelector(kn).innerHTML,
            this.otherTemplate = this.wrapper.querySelector(An).innerHTML,
            this.titleTemplate = this.wrapper.querySelector(qn).innerHTML,
            this.ariaTemplate = this.wrapper.querySelector(xn).innerHTML,
            this.productTitleWrapper = this.results.querySelector(_n),
            this.productWrapper = this.results.querySelector(Pn),
            this.collectionWrapper = this.results.querySelector(Cn),
            this.articleWrapper = this.results.querySelector(Dn),
            this.pageWrapper = this.results.querySelector(Mn),
            this.ariaWrapper = this.results.querySelector(Hn),
            this.initSearch()
        }
        initSearch() {
            this.input.addEventListener("input", _(function(t) {
                const e = t.target.value;
                e && e.length > 1 ? (this.loader.style.display = "block",
                this.render(e)) : (this.resetTemplates(),
                this.outer.classList.remove($n))
            }
            .bind(this), 300)),
            this.input.addEventListener("clear", this.reset.bind(this))
        }
        render(t) {
            let e = "";
            e += window.theme.settings.search_products ? "product," : "",
            e += window.theme.settings.search_collections ? "collection," : "",
            e += window.theme.settings.search_articles ? "article," : "",
            e += window.theme.settings.search_pages ? "page," : "",
            e = e.slice(0, -1);
            fetch(`/search/suggest.json?q=${t}&resources[type]=${e}&resources[options][unavailable_products]=last`).then(this.handleErrors).then((t=>t.json())).then((e=>{
                this.resetTemplates(),
                this.outer.classList.add($n);
                const i = e.resources.results
                  , s = [];
                for (const t in i)
                    ({}).hasOwnProperty.call(i, t) && s.push(...i[t]);
                s.length ? (this.outer.classList.remove(Fn),
                this.injectOther(i),
                this.injectProduct(i.products)) : this.noResults(t),
                this.injectAria(t, s),
                Wt(this.outer, {
                    elementToFocus: this.input
                })
            }
            )).catch((t=>{
                console.error(t)
            }
            )).finally((()=>{
                this.loader.style.display = "none"
            }
            ))
        }
        injectAria(t, e) {
            let i = window.theme.strings.noResultsFor
              , s = null;
            e.length && (s = e.length,
            i = window.theme.strings.resultsFor),
            this.ariaWrapper.innerHTML = m.render(this.ariaTemplate, {
                count: s,
                title: i,
                query: t
            })
        }
        noResults() {
            this.resetTemplates(),
            this.outer.classList.add($n),
            this.outer.classList.add(Fn)
        }
        resetTemplates() {
            this.productTitleWrapper.innerHTML = "",
            this.collectionWrapper.innerHTML = "",
            this.articleWrapper.innerHTML = "",
            this.productWrapper.innerHTML = "",
            this.pageWrapper.innerHTML = "",
            this.ariaWrapper.innerHTML = ""
        }
        reset() {
            this.resetTemplates(),
            this.outer.classList.remove($n),
            this.outer.classList.remove(Fn),
            this.input.val = ""
        }
        injectOther(t) {
            this.productTitleWrapper.innerHTML += m.render(this.titleTemplate, {
                title: window.theme.strings.products,
                count: t.products.length
            }),
            t.collections && t.collections.length && (this.collectionWrapper.innerHTML += m.render(this.titleTemplate, {
                title: window.theme.strings.collections,
                count: t.collections.length
            }),
            this.collectionWrapper.innerHTML += m.render(this.otherTemplate, t.collections)),
            t.pages && t.pages.length && (this.pageWrapper.innerHTML += m.render(this.titleTemplate, {
                title: window.theme.strings.pages,
                count: t.pages.length
            }),
            this.pageWrapper.innerHTML += m.render(this.otherTemplate, t.pages)),
            t.articles && t.articles.length && (this.articleWrapper.innerHTML += m.render(this.titleTemplate, {
                title: window.theme.strings.articles,
                count: t.articles.length
            }),
            this.articleWrapper.innerHTML += m.render(this.otherTemplate, t.articles))
        }
        injectProduct(t) {
            let e = [];
            t.forEach((t=>{
                let i = t;
                i = function(t) {
                    const e = t.price < t.compare_at_price_min;
                    let i = e ? bn : "";
                    if (i += t.available ? "" : Sn,
                    t.price = n.formatMoney(t.price, theme.moneyFormat),
                    t.prive_varies) {
                        let e = n.formatMoney(t.price_min, theme.moneyFormat);
                        t.price = `${window.theme.strings.from} ${e}`
                    }
                    return {
                        ...t,
                        classes: i,
                        on_sale: e,
                        sold_out: !t.available,
                        sold_out_translation: window.theme.strings.sold,
                        compare_at_price: n.formatMoney(t.compare_at_price_min, theme.moneyFormat),
                        compare_at_price_max: n.formatMoney(t.compare_at_price_max, theme.moneyFormat),
                        compare_at_price_min: n.formatMoney(t.compare_at_price_min, theme.moneyFormat),
                        price_max: n.formatMoney(t.price_max, theme.moneyFormat),
                        price_min: n.formatMoney(t.price_min, theme.moneyFormat)
                    }
                }(i),
                i.image = null,
                i.featured_image && (i.thumb = Bi(i.featured_image.url, "360x360")),
                e.push(i)
            }
            ));
            const i = m.render(this.productTemplate, e);
            this.productWrapper.innerHTML += i
        }
        handleErrors(t) {
            return t.ok ? t : t.json().then((function(e) {
                throw new O({
                    status: t.statusText,
                    headers: t.headers,
                    json: e
                })
            }
            ))
        }
    }
    const jn = {
        onLoad() {
            On[this.id] = [];
            document.querySelectorAll(En).forEach((t=>{
                On[this.id].push(new Wn(t))
            }
            ))
        },
        onUnload: function() {
            On[this.id].forEach((t=>{
                "function" == typeof t.unload && t.unload()
            }
            ))
        }
    }
      , Nn = "[data-drawer-search]"
      , zn = "[data-search-popdown-wrap]"
      , Vn = "[data-predictive-search-input]"
      , Rn = "[data-clear-input]";
    class Un {
        constructor(t) {
            this.outer = t.container.querySelector(Nn),
            this.outer && (this.wrapper = this.outer.querySelector(zn),
            this.input = this.outer.querySelector(Vn),
            this.clear = this.outer.querySelector(Rn),
            this.init())
        }
        init() {
            this.clear.addEventListener("click", function(t) {
                t.preventDefault(),
                this.clearInput()
            }
            .bind(this))
        }
        clearInput() {
            this.input.value = "",
            this.input.dispatchEvent(new CustomEvent("clear",{
                bubbles: !1
            })),
            this.input.focus()
        }
    }
    const Jn = {
        onLoad() {
            this.searchDrawer = new Un(this)
        },
        onUnload: function() {
            this.searchDrawer && "function" == typeof this.searchDrawer.unload && this.searchDrawer.unload()
        }
    }
      , Kn = "[data-popout]"
      , Xn = "[data-popout-list]"
      , Yn = "[data-popout-toggle]"
      , Qn = "[data-popout-input]"
      , Gn = "[data-popout-option]"
      , Zn = "data-popout-prevent"
      , to = "data-quantity-field"
      , eo = "data-value"
      , io = "aria-expanded"
      , so = "aria-current"
      , no = "popout-list--visible"
      , oo = "--current";
    let ro = {};
    class ao {
        constructor(t) {
            this.container = t,
            this.popoutList = this.container.querySelector(Xn),
            this.popoutToggle = this.container.querySelector(Yn),
            this.popoutInput = this.container.querySelector(Qn),
            this.popoutOptions = this.container.querySelectorAll(Gn),
            this.popoutPrevent = "true" === this.container.getAttribute(Zn),
            this._connectOptions(),
            this._connectToggle(),
            this._onFocusOut(),
            this.popoutInput && this.popoutInput.hasAttribute(to) && document.addEventListener("popout:updateValue", this.updatePopout.bind(this))
        }
        unload() {
            this.popoutOptions.length && this.popoutOptions.forEach((t=>{
                t.removeEventListener("clickDetails", this.popupOptionsClick.bind(this)),
                t.removeEventListener("click", this._connectOptionsDispatch.bind(this))
            }
            )),
            this.popoutToggle.removeEventListener("click", this.popupToggleClick.bind(this)),
            this.popoutToggle.removeEventListener("focusout", this.popupToggleFocusout.bind(this)),
            this.popoutList.removeEventListener("focusout", this.popupListFocusout.bind(this)),
            this.container.removeEventListener("keyup", this.containerKeyup.bind(this))
        }
        popupToggleClick(t) {
            const e = "true" === t.currentTarget.getAttribute(io);
            t.currentTarget.setAttribute(io, !e),
            this.popoutList.classList.toggle(no)
        }
        popupToggleFocusout(t) {
            this.container.contains(t.relatedTarget) || this._hideList()
        }
        popupListFocusout(t) {
            const e = t.currentTarget.contains(t.relatedTarget);
            this.popoutList.classList.contains(no) && !e && this._hideList()
        }
        popupOptionsClick(t) {
            if ("#" === t.target.closest(Gn).attributes.href.value) {
                t.preventDefault();
                let e = "";
                if (t.currentTarget.getAttribute(eo) && (e = t.currentTarget.getAttribute(eo)),
                this.popoutInput.value = e,
                this.popoutPrevent) {
                    this.popoutInput.dispatchEvent(new Event("change")),
                    !t.detail.preventTrigger && this.popoutInput.hasAttribute(to) && this.popoutInput.dispatchEvent(new Event("input"));
                    const i = this.popoutList.querySelector(`[class*="${oo}"]`);
                    let s = oo;
                    if (i && i.classList.length)
                        for (const t of i.classList)
                            if (t.includes(oo)) {
                                s = t;
                                break
                            }
                    const n = this.popoutList.querySelector("." + s);
                    n && (n.classList.remove("" + s),
                    t.currentTarget.parentElement.classList.add("" + s));
                    const o = this.popoutList.querySelector(`[${so}]`);
                    o && o.hasAttribute("" + so) && (o.removeAttribute("" + so),
                    t.currentTarget.setAttribute("" + so, "true")),
                    "" !== e && (this.popoutToggle.textContent = e),
                    this.popupToggleFocusout(t),
                    this.popupListFocusout(t)
                } else
                    this._submitForm(e)
            }
        }
        updatePopout(t) {
            const e = this.popoutList.querySelector(`[${eo}="${this.popoutInput.value}"]`);
            e && e.dispatchEvent(new CustomEvent("clickDetails",{
                cancelable: !0,
                bubbles: !0,
                detail: {
                    preventTrigger: !0
                }
            }))
        }
        containerKeyup(t) {
            t.which === window.theme.keyboardKeys.ESCAPE && (this._hideList(),
            this.popoutToggle.focus())
        }
        bodyClick(t) {
            const e = this.container.contains(t.target);
            this.popoutList.classList.contains(no) && !e && this._hideList()
        }
        _connectToggle() {
            this.popoutToggle.addEventListener("click", this.popupToggleClick.bind(this))
        }
        _connectOptions() {
            this.popoutOptions.length && this.popoutOptions.forEach((t=>{
                t.addEventListener("clickDetails", this.popupOptionsClick.bind(this)),
                t.addEventListener("click", this._connectOptionsDispatch.bind(this))
            }
            ))
        }
        _connectOptionsDispatch(t) {
            const e = new CustomEvent("clickDetails",{
                cancelable: !0,
                bubbles: !0,
                detail: {
                    preventTrigger: !1
                }
            });
            t.target.dispatchEvent(e) || t.preventDefault()
        }
        _onFocusOut() {
            this.popoutToggle.addEventListener("focusout", this.popupToggleFocusout.bind(this)),
            this.popoutList.addEventListener("focusout", this.popupListFocusout.bind(this)),
            this.container.addEventListener("keyup", this.containerKeyup.bind(this)),
            document.body.addEventListener("click", this.bodyClick.bind(this))
        }
        _submitForm(t) {
            const e = this.container.closest("form");
            e && e.submit()
        }
        _hideList() {
            this.popoutList.classList.remove(no),
            this.popoutToggle.setAttribute(io, !1)
        }
    }
    const lo = {
        onLoad() {
            ro[this.id] = [];
            this.container.querySelectorAll(Kn).forEach((t=>{
                ro[this.id].push(new ao(t))
            }
            ))
        },
        onUnload() {
            ro[this.id].forEach((t=>{
                "function" == typeof t.unload && t.unload()
            }
            ))
        }
    }
      , co = {
        slideruleOpen: "data-sliderule-open",
        slideruleClose: "data-sliderule-close",
        sliderulePane: "data-sliderule-pane",
        slideruleWrappper: "[data-sliderule]",
        focusable: 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
        children: ":scope > [data-animates], \n             :scope > * > [data-animates], \n             :scope > * > * >[data-animates],\n             :scope > .sliderule-grid  > *"
    }
      , ho = "is-visible";
    let uo = {};
    class po {
        constructor(t) {
            this.sliderule = t,
            this.wrapper = t.closest(co.wrapper),
            this.key = this.sliderule.id;
            const e = `[${co.slideruleOpen}='${this.key}']`
              , i = `[${co.slideruleClose}='${this.key}']`;
            this.trigger = document.querySelector(e),
            this.exit = document.querySelector(i),
            this.pane = document.querySelector(`[${co.sliderulePane}]`),
            this.children = this.sliderule.querySelectorAll(co.children),
            this.trigger.setAttribute("aria-haspopup", !0),
            this.trigger.setAttribute("aria-expanded", !1),
            this.trigger.setAttribute("aria-controls", this.key),
            this.clickEvents(),
            this.staggerChildAnimations(),
            document.addEventListener("theme:sliderule:close", (()=>this.closeSliderule()))
        }
        clickEvents() {
            this.trigger.addEventListener("click", function() {
                this.showSliderule()
            }
            .bind(this)),
            this.exit.addEventListener("click", function() {
                this.hideSliderule()
            }
            .bind(this))
        }
        keyboardEvents() {
            this.trigger.addEventListener("keyup", function(t) {
                t.which === window.theme.keyboardKeys.SPACE && this.showSliderule()
            }
            .bind(this)),
            this.sliderule.addEventListener("keyup", function(t) {
                t.which === window.theme.keyboardKeys.ESCAPE && (this.hideSliderule(),
                this.buttons[0].focus())
            }
            .bind(this))
        }
        staggerChildAnimations() {
            this.children.forEach(((t,e)=>{
                t.style.transitionDelay = 50 * e + 10 + "ms"
            }
            ))
        }
        hideSliderule() {
            this.sliderule.classList.remove(ho),
            this.children.forEach((t=>{
                t.classList.remove(ho)
            }
            ));
            const t = parseInt(this.pane.dataset.sliderulePane, 10) - 1;
            this.pane.setAttribute(co.sliderulePane, t)
        }
        showSliderule() {
            this.sliderule.classList.add(ho),
            this.children.forEach((t=>{
                t.classList.add(ho)
            }
            ));
            const t = parseInt(this.pane.dataset.sliderulePane, 10) + 1;
            this.pane.setAttribute(co.sliderulePane, t)
        }
        closeSliderule() {
            this.pane && this.pane.hasAttribute(co.sliderulePane) && parseInt(this.pane.getAttribute(co.sliderulePane)) > 0 && (this.hideSliderule(),
            parseInt(this.pane.getAttribute(co.sliderulePane)) > 0 && this.pane.setAttribute(co.sliderulePane, 0))
        }
    }
    const mo = {
        onLoad() {
            uo[this.id] = [];
            this.container.querySelectorAll(co.slideruleWrappper).forEach((t=>{
                uo[this.id].push(new po(t))
            }
            ))
        },
        onUnload: function() {
            uo[this.id].forEach((t=>{
                "function" == typeof t.unload && t.unload()
            }
            ))
        }
    }
      , yo = "[data-product-add-popdown-wrapper]"
      , fo = "[data-close-popdown]"
      , go = '[data-ajax-disable="false"]'
      , wo = '[data-ajax-disable="true"]';
    var vo;
    class bo {
        constructor() {
            this.drawer = document.querySelector(yo),
            this.cartSectionAjax = document.querySelector(go),
            this.ajaxDisabled = document.querySelector(wo),
            document.addEventListener("theme:cart:popdown", (t=>{
                this.cartSectionAjax ? this.cartSectionAjax.dispatchEvent(new CustomEvent("theme:cart:reload",{
                    bubbles: !0
                })) : this.ajaxDisabled ? window.location.reload() : this.renderPopdown(t)
            }
            ))
        }
        renderPopdown(t) {
            const e = t.detail.variant
              , i = `${window.theme.routes.root_url}variants/${e.id}/?section_id=api-product-popdown`
              , s = this;
            a.get(i).then((function(t) {
                const e = document.createElement("div");
                e.innerHTML = t.data,
                s.drawer.innerHTML = e.querySelector("[data-api-content]").innerHTML,
                s.connectCartButton(),
                s.connectCloseButton()
            }
            )).catch((function(t) {
                console.warn(t)
            }
            ))
        }
        connectCloseButton() {
            this.drawer.classList.add("is-visible");
            this.drawer.querySelector(fo).addEventListener("click", function(t) {
                t.preventDefault(),
                this.drawer.classList.remove("is-visible")
            }
            .bind(this)),
            this.popdownTimer()
        }
        connectCartButton() {
            const t = this.drawer.querySelector('[data-drawer-toggle="drawer-cart"]')
              , e = document.querySelector('[data-drawer="drawer-cart"]');
            e && t.addEventListener("click", function(t) {
                t.preventDefault(),
                this.drawer.classList.remove("is-visible"),
                e.dispatchEvent(new CustomEvent("theme:drawer:open",{
                    bubbles: !1
                }))
            }
            .bind(this))
        }
        popdownTimer() {
            clearTimeout(vo),
            vo = setTimeout((()=>{
                this.drawer.classList.remove("is-visible")
            }
            ), 5e3)
        }
    }
    const So = {
        onLoad() {
            new bo(this)
        }
    }
      , Eo = "[data-takes-space]"
      , Lo = "[data-header-desktop]"
      , To = "js__header__clone"
      , ko = "js__show__mobile"
      , Ao = "[data-header-backfill]"
      , qo = "data-header-transparent"
      , xo = "header-override-border"
      , _o = ".main-content > .shopify-section:first-child [data-overlay-header]"
      , Po = ".main-content > .shopify-section:first-child [data-prevent-transparent-header]"
      , Co = '.navlink[href="#"]';
    let Do = {};
    class Mo {
        constructor(t) {
            this.wrapper = t,
            this.style = this.wrapper.dataset.style,
            this.desktop = this.wrapper.querySelector(Lo),
            this.transparent = "false" !== this.wrapper.getAttribute(qo),
            this.overlayedImages = document.querySelectorAll(_o),
            this.deadLinks = document.querySelectorAll(Co),
            this.killDeadLinks(),
            "drawer" !== this.style && this.desktop && (this.minWidth = this.getMinWidth(),
            this.listenWidth()),
            this.checkForImage(),
            window.dispatchEvent(new Event("resize")),
            document.addEventListener("header:check", this.checkForImage.bind(this))
        }
        unload() {
            document.removeEventListener("theme:resize", this.checkWidth)
        }
        checkForImage() {
            this.overlayedImages = document.querySelectorAll(_o);
            let t = document.querySelectorAll(Po).length;
            this.overlayedImages.length && !t && this.transparent ? (document.querySelector(Ao).style.display = "none",
            this.listenOverlay()) : this.wrapper.setAttribute(qo, !1),
            !this.overlayedImages.length || t || this.transparent || (this.wrapper.classList.add(xo),
            this.subtractHeaderHeight())
        }
        listenOverlay() {
            document.addEventListener("theme:resize", this.checkWidth.bind(this)),
            this.subtractAnnouncementHeight()
        }
        listenWidth() {
            document.addEventListener("theme:resize", this.checkWidth.bind(this)),
            this.checkWidth()
        }
        killDeadLinks() {
            this.deadLinks.forEach((t=>{
                t.onclick = t=>{
                    t.preventDefault()
                }
            }
            ))
        }
        subtractAnnouncementHeight() {
            const {windowHeight: t, announcementHeight: e} = E();
            this.overlayedImages.forEach((i=>{
                i.style.setProperty("--full-screen", t - e + "px"),
                i.classList.add("has-overlay")
            }
            ))
        }
        subtractHeaderHeight() {
            const {windowHeight: t, headerHeight: e} = E();
            this.overlayedImages.forEach((i=>{
                i.style.setProperty("--full-screen", t - e + "px")
            }
            ))
        }
        checkWidth() {
            document.body.clientWidth < this.minWidth ? this.wrapper.classList.add(ko) : this.wrapper.classList.remove(ko)
        }
        getMinWidth() {
            const t = this.wrapper.cloneNode(!0);
            t.classList.add(To),
            document.body.appendChild(t);
            const e = t.querySelectorAll(Eo);
            let i = 0;
            return i = 3 === e.length ? function(t) {
                let e = [];
                t.forEach((t=>{
                    e.push(t.clientWidth)
                }
                )),
                e[0] > e[2] ? e[2] = e[0] : e[0] = e[2];
                return e.reduce(((t,e)=>t + e))
            }(e) : function(t) {
                let e = 0;
                return t.forEach((t=>{
                    e += t.clientWidth
                }
                )),
                e
            }(e),
            document.body.removeChild(t),
            i + 20 * e.length
        }
    }
    Pt("header", [{
        onLoad() {
            Do = new Mo(this.container)
        },
        onUnload: function() {
            "function" == typeof Do.unload && Do.unload()
        }
    }, Oe, lo, mo, Xe, ci, bi, ki, Ii, jn, Jn, us, cn, So, vn]);
    Pt("footer", [lo, {
        onLoad() {
            var t = document.querySelector("[data-powered-link] a");
            t && t.relList.add("noopener")
        }
    }, vn]);
    var Ho = !1;
    function Io() {
        return Ho
    }
    document.addEventListener("touchstart", (function t() {
        Ho = !0,
        document.removeEventListener("touchstart", t, {
            passive: !0
        }),
        document.querySelector("body").classList.add("supports-touch"),
        document.dispatchEvent(new CustomEvent("theme:touch",{
            bubbles: !0
        }))
    }
    ), {
        passive: !0
    });
    const Bo = {
        cc_load_policy: 1,
        iv_load_policy: 3,
        modestbranding: 1,
        playsinline: 1,
        controls: 1,
        showinfo: 0,
        ecver: 2,
        fs: 1,
        rel: 0
    };
    function $o(t, e) {
        const i = {
            ...Bo,
            ...e
        }
          , s = document.querySelector(`[data-player="${t}"]`)
          , n = s.querySelector("iframe, [data-replace]")
          , o = s.querySelector("[data-video-id]").getAttribute("data-video-id");
        Ki({
            url: "https://www.youtube.com/iframe_api"
        });
        return window.youtubeLoaderPromise.then((function() {
            let t = new window.YT.Player(n,{
                videoId: o,
                playerVars: {
                    ...i
                }
            });
            return s.addEventListener("pause", (function() {
                try {
                    t.pauseVideo && t.pauseVideo()
                } catch (t) {
                    console.warn(t)
                }
            }
            )),
            s.addEventListener("play-desktop", (function() {
                Io() || s.dispatchEvent(new Event("play"))
            }
            )),
            s.addEventListener("play", (function() {
                try {
                    t.playVideo ? t.playVideo() : t.addEventListener("onReady", (function(t) {
                        t.target.playVideo()
                    }
                    ))
                } catch (t) {
                    console.warn(t)
                }
            }
            )),
            s.addEventListener("destroy", (function() {
                try {
                    t.destroy && t.destroy()
                } catch (t) {
                    console.warn(t)
                }
            }
            )),
            t
        }
        )).catch((function(t) {
            console.error(t)
        }
        ))
    }
    window.youtubeLoaderPromise = new Promise((t=>{
        window.onYouTubeIframeAPIReady = function() {
            t()
        }
    }
    ));
    const Fo = {
        autoplay: !0,
        loop: !0,
        controls: !0,
        muted: !1,
        playsinline: !0
    };
    const Oo = "[data-video-popup]"
      , Wo = "[data-video-autoplay]"
      , jo = "data-unique"
      , No = "data-video-id"
      , zo = "data-video-type"
      , Vo = "data-player";
    class Ro {
        constructor(t) {
            this.container = t.container,
            this.triggers = this.container.querySelectorAll(Oo),
            this.backgroundVideo = this.container.querySelector(Wo),
            this.init()
        }
        init() {
            this.triggers.forEach((t=>{
                const i = t.getAttribute(jo)
                  , s = t.getAttribute(No)
                  , n = t.getAttribute(zo)
                  , o = `${s}-${i}`
                  , r = document.querySelector(`[${Vo}="${o}"]`);
                e.init({
                    onShow: ()=>{
                        this.backgroundVideo && "function" == typeof this.backgroundVideo.pause && this.backgroundVideo.pause();
                        let t = {};
                        "youtube" === n ? t = $o(o) : "vimeo" === n && (t = function(t, e) {
                            const i = {
                                ...Fo,
                                ...e
                            }
                              , s = document.querySelector(`[data-player="${t}"]`)
                              , n = s.querySelector("iframe, [data-replace]")
                              , o = s.querySelector("[data-video-id]").getAttribute("data-video-id")
                              , r = Ki({
                                url: "https://player.vimeo.com/api/player.js"
                            })
                              , a = "select-" + t;
                            return n.setAttribute("id", a),
                            r.then((function() {
                                const t = new window.Vimeo.Player(a,{
                                    ...i,
                                    id: o
                                });
                                return s.addEventListener("pause", (function() {
                                    try {
                                        t.pause && t.pause()
                                    } catch (t) {
                                        console.warn(t)
                                    }
                                }
                                )),
                                s.addEventListener("play-desktop", (function() {
                                    Io() || s.dispatchEvent(new Event("play"))
                                }
                                )),
                                s.addEventListener("play", (function() {
                                    t.play && t.play()
                                }
                                )),
                                s.addEventListener("destroy", (function() {
                                    try {
                                        t.destroy && t.destroy()
                                    } catch (t) {
                                        console.log(t)
                                    }
                                }
                                )),
                                t
                            }
                            )).catch((function(t) {
                                console.error(t)
                            }
                            ))
                        }(o)),
                        t.then((()=>{
                            r.dispatchEvent(new CustomEvent("play"))
                        }
                        ))
                    }
                    ,
                    onClose: (t,e,i)=>{
                        i.preventDefault(),
                        r.dispatchEvent(new CustomEvent("destroy")),
                        this.backgroundVideo && "function" == typeof this.backgroundVideo.play && this.backgroundVideo.play()
                    }
                    ,
                    openTrigger: `data-trigger-${s}-${i}`
                })
            }
            ))
        }
    }
    const Uo = {
        onLoad() {
            new Ro(this)
        }
    }
      , Jo = "[data-scroll-down]";
    class Ko {
        constructor(t) {
            this.wrapper = t,
            this.init()
        }
        init() {
            const t = this.wrapper.querySelectorAll(Jo);
            t && t.forEach((t=>{
                t.addEventListener("click", this.scroll.bind(this))
            }
            ))
        }
        scroll() {
            const t = this.wrapper.offsetTop + this.wrapper.clientHeight;
            window.scroll({
                top: t,
                left: 0,
                behavior: "smooth"
            })
        }
    }
    const Xo = {
        onLoad() {
            this.scrollButton = new Ko(this.container)
        },
        onUnload: function() {
            delete this.scrollButton
        }
    };
    Pt("video", [Xt, Xo, Uo]),
    Pt("page-faq", vn),
    Pt("hero", [Xt, Xo]);
    const Yo = "[data-slider]"
      , Qo = "[data-grid-slide]"
      , Go = "data-show-dots"
      , Zo = {};
    class tr {
        constructor(t, e) {
            this.container = t,
            this.slideshow = e,
            this.pageDots = "true" === this.slideshow.getAttribute(Go),
            this.firstPhoto = this.container.querySelector(Qo);
            const i = this.firstPhoto.offsetHeight / 2;
            this.slideshow.style.setProperty("--buttons-top", i + "px"),
            this.slideshow && (this.flkty = null,
            this.init())
        }
        init() {
            const t = this
              , e = {
                initialIndex: 0,
                accessibility: !0,
                autoPlay: !1,
                contain: !0,
                pageDots: this.pageDots,
                adaptiveHeight: !1,
                wrapAround: !1,
                groupCells: !0,
                cellAlign: "left",
                freeScroll: !0,
                prevNextButtons: !0,
                draggable: !0,
                arrowShape: {
                    x0: 10,
                    x1: 60,
                    y1: 50,
                    x2: 65,
                    y2: 45,
                    x3: 20
                },
                on: {
                    ready: function() {
                        t.removeIncorrectAria()
                    }
                }
            };
            this.flkty = new s(this.slideshow,e),
            this.container.addEventListener("theme:tab:change", (()=>{
                this.flkty.resize()
            }
            ))
        }
        removeIncorrectAria() {
            this.slideshow.querySelectorAll('[aria-hidden="true"]').forEach((t=>t.removeAttribute("aria-hidden")))
        }
        onUnload() {
            this.slideshow && this.flkty && (this.flkty.options.watchCSS = !1,
            this.flkty.destroy())
        }
    }
    const er = {
        onLoad() {
            Zo[this.id] = [];
            this.container.querySelectorAll(Yo).forEach((t=>{
                Zo[this.id].push(new tr(this.container,t))
            }
            ))
        },
        onUnload(t) {
            Zo[this.id].forEach((e=>{
                "function" == typeof e.onUnload && e.onUnload(t)
            }
            ))
        }
    };
    Pt("custom-content", [Xt, Uo, us, er]);
    const ir = []
      , sr = "[data-slideshow-wrapper]"
      , nr = "data-slideshow-speed"
      , or = "data-slideshow-autoplay"
      , rr = "data-slideshow-slides"
      , ar = "[data-slide-custom-prev]"
      , lr = "[data-slide-custom-next]";
    class cr {
        constructor(t) {
            this.wrapper = t.container.querySelector(sr),
            this.speed = this.wrapper.getAttribute(nr),
            this.autoplay = "true" === this.wrapper.getAttribute(or),
            this.slideCount = parseInt(this.wrapper.getAttribute(rr), 10),
            this.prevButtons = this.wrapper.querySelectorAll(ar),
            this.nextButtons = this.wrapper.querySelectorAll(lr),
            this.flkty = null,
            this.init()
        }
        init() {
            const t = {
                autoPlay: !(!this.autoplay || !this.speed) && parseInt(this.speed),
                contain: !1,
                pageDots: !0,
                adaptiveHeight: !0,
                accessibility: !0,
                wrapAround: 2 !== this.slideCount,
                prevNextButtons: !1,
                draggable: !0,
                fade: !0
            };
            this.flkty = new l(this.wrapper,t),
            this.prevButtons.length && this.prevButtons.forEach((t=>{
                t.onclick = ()=>{
                    this.flkty.previous(!0, !1)
                }
            }
            )),
            this.nextButtons.length && this.nextButtons.forEach((t=>{
                t.onclick = ()=>{
                    this.flkty.next(!0, !1)
                }
            }
            ))
        }
        unload() {
            this.flkty.destroy()
        }
        onBlockSelect(t) {
            const e = t.target.closest("[data-slideshow-index]").getAttribute("data-slideshow-index")
              , i = parseInt(e);
            this.flkty.selectCell(i),
            this.flkty.stopPlayer()
        }
        onBlockDeselect() {
            this.autoplay && this.flkty.playPlayer()
        }
    }
    Pt("slideshow", [{
        onLoad() {
            ir[this.id] = new cr(this)
        },
        onUnload() {
            "function" == typeof ir[this.id].unload && ir[this.id].unload()
        },
        onBlockSelect(t) {
            "function" == typeof ir[this.id].onBlockSelect && ir[this.id].onBlockSelect(t)
        },
        onBlockDeselect(t) {
            "function" == typeof ir[this.id].onBlockSelect && ir[this.id].onBlockDeselect(t)
        }
    }, Xt, Xo]);
    const hr = "[data-range-slider]"
      , dr = "[data-range-left]"
      , ur = "[data-range-right]"
      , pr = "[data-range-line]"
      , mr = "[data-range-holder]"
      , yr = "data-se-min"
      , fr = "data-se-max"
      , gr = "data-se-min-value"
      , wr = "data-se-max-value"
      , vr = "data-se-step"
      , br = "data-range-filter-update"
      , Sr = "[data-field-price-min]"
      , Er = "[data-field-price-max]"
      , Lr = "is-initialized";
    class Tr {
        constructor(t) {
            this.container = t.container,
            this.slider = t.querySelector(hr),
            this.slider && (this.onMoveEvent = t=>this.onMove(t),
            this.onStopEvent = t=>this.onStop(t),
            this.onStartEvent = t=>this.onStart(t),
            this.startX = 0,
            this.x = 0,
            this.touchLeft = this.slider.querySelector(dr),
            this.touchRight = this.slider.querySelector(ur),
            this.lineSpan = this.slider.querySelector(pr),
            this.min = parseFloat(this.slider.getAttribute(yr)),
            this.max = parseFloat(this.slider.getAttribute(fr)),
            this.step = 0,
            this.normalizeFact = 26,
            this.init(),
            document.addEventListener("theme:reset-price-range", (()=>{
                this.setDefaultValues()
            }
            )))
        }
        init() {
            this.setDefaultValues(),
            this.touchLeft.addEventListener("mousedown", this.onStartEvent),
            this.touchRight.addEventListener("mousedown", this.onStartEvent),
            this.touchLeft.addEventListener("touchstart", this.onStartEvent),
            this.touchRight.addEventListener("touchstart", this.onStartEvent),
            this.slider.classList.add(Lr)
        }
        setDefaultValues() {
            let t = this.min;
            this.slider.hasAttribute(gr) && (t = parseFloat(this.slider.getAttribute(gr)));
            let e = this.max;
            this.slider.hasAttribute(wr) && (e = parseFloat(this.slider.getAttribute(wr))),
            t < this.min && (t = this.min),
            e > this.max && (e = this.max),
            t > e && (t = e),
            this.slider.getAttribute(vr) && (this.step = Math.abs(parseFloat(this.slider.getAttribute(vr)))),
            this.reset(),
            this.maxX = this.slider.offsetWidth - this.touchRight.offsetWidth,
            this.selectedTouch = null,
            this.initialValue = this.lineSpan.offsetWidth - this.normalizeFact,
            this.setMinValue(t),
            this.setMaxValue(e)
        }
        reset() {
            this.touchLeft.style.left = "0px",
            this.touchRight.style.left = this.slider.offsetWidth - this.touchLeft.offsetWidth + "px",
            this.lineSpan.style.marginLeft = "0px",
            this.lineSpan.style.width = this.slider.offsetWidth - this.touchLeft.offsetWidth + "px",
            this.startX = 0,
            this.x = 0
        }
        setMinValue(t) {
            const e = (t - this.min) / (this.max - this.min);
            this.touchLeft.style.left = Math.ceil(e * (this.slider.offsetWidth - (this.touchLeft.offsetWidth + this.normalizeFact))) + "px",
            this.lineSpan.style.marginLeft = this.touchLeft.offsetLeft + "px",
            this.lineSpan.style.width = this.touchRight.offsetLeft - this.touchLeft.offsetLeft + "px",
            this.slider.setAttribute(gr, t)
        }
        setMaxValue(t) {
            const e = (t - this.min) / (this.max - this.min);
            this.touchRight.style.left = Math.ceil(e * (this.slider.offsetWidth - (this.touchLeft.offsetWidth + this.normalizeFact)) + this.normalizeFact) + "px",
            this.lineSpan.style.marginLeft = this.touchLeft.offsetLeft + "px",
            this.lineSpan.style.width = this.touchRight.offsetLeft - this.touchLeft.offsetLeft + "px",
            this.slider.setAttribute(wr, t)
        }
        onStart(t) {
            t.preventDefault();
            let e = t;
            t.touches && (e = t.touches[0]),
            t.currentTarget === this.touchLeft ? this.x = this.touchLeft.offsetLeft : this.x = this.touchRight.offsetLeft,
            this.startX = e.pageX - this.x,
            this.selectedTouch = t.currentTarget,
            this.slider.addEventListener("mousemove", this.onMoveEvent),
            this.slider.addEventListener("mouseup", this.onStopEvent),
            this.slider.addEventListener("touchmove", this.onMoveEvent),
            this.slider.addEventListener("touchend", this.onStopEvent)
        }
        onMove(t) {
            let e = t;
            if (t.touches && (e = t.touches[0]),
            this.x = e.pageX - this.startX,
            this.selectedTouch === this.touchLeft ? (this.x > this.touchRight.offsetLeft - this.selectedTouch.offsetWidth + 10 ? this.x = this.touchRight.offsetLeft - this.selectedTouch.offsetWidth + 10 : this.x < 0 && (this.x = 0),
            this.selectedTouch.style.left = this.x + "px") : this.selectedTouch === this.touchRight && (this.x < this.touchLeft.offsetLeft + this.touchLeft.offsetWidth - 10 ? this.x = this.touchLeft.offsetLeft + this.touchLeft.offsetWidth - 10 : this.x > this.maxX && (this.x = this.maxX),
            this.selectedTouch.style.left = this.x + "px"),
            this.lineSpan.style.marginLeft = this.touchLeft.offsetLeft + "px",
            this.lineSpan.style.width = this.touchRight.offsetLeft - this.touchLeft.offsetLeft + "px",
            this.calculateValue(),
            this.slider.getAttribute("on-change")) {
                new Function("min, max",this.slider.getAttribute("on-change"))(this.slider.getAttribute(gr), this.slider.getAttribute(wr))
            }
            this.onChange(this.slider.getAttribute(gr), this.slider.getAttribute(wr))
        }
        onStop(t) {
            this.slider.removeEventListener("mousemove", this.onMoveEvent),
            this.slider.removeEventListener("mouseup", this.onStopEvent),
            this.slider.removeEventListener("touchmove", this.onMoveEvent),
            this.slider.removeEventListener("touchend", this.onStopEvent),
            this.selectedTouch = null,
            this.calculateValue(),
            this.onChanged(this.slider.getAttribute(gr), this.slider.getAttribute(wr))
        }
        onChange(t, e) {
            const i = this.slider.closest(mr);
            if (i) {
                const s = i.querySelector(Sr)
                  , n = i.querySelector(Er);
                s && n && (s.value = t,
                n.value = e)
            }
        }
        onChanged(t, e) {
            this.slider.hasAttribute(br) && this.slider.dispatchEvent(new CustomEvent("range:filter:update",{
                bubbles: !0
            }))
        }
        calculateValue() {
            const t = (this.lineSpan.offsetWidth - this.normalizeFact) / this.initialValue;
            let e = this.lineSpan.offsetLeft / this.initialValue
              , i = e + t;
            if (e = e * (this.max - this.min) + this.min,
            i = i * (this.max - this.min) + this.min,
            0 !== this.step) {
                let t = Math.floor(e / this.step);
                e = this.step * t,
                t = Math.floor(i / this.step),
                i = this.step * t
            }
            this.selectedTouch === this.touchLeft && this.slider.setAttribute(gr, e),
            this.selectedTouch === this.touchRight && this.slider.setAttribute(wr, i)
        }
    }
    const kr = "[data-sidebar-filter-form]"
      , Ar = "input, select, label, textarea"
      , qr = "[data-field-price-min]"
      , xr = "[data-field-price-max]"
      , _r = "data-field-price-min"
      , Pr = "data-field-price-max"
      , Cr = "[data-se-min-value]"
      , Dr = "[data-se-max-value]"
      , Mr = "data-se-min-value"
      , Hr = "data-se-max-value";
    class Ir {
        constructor(t) {
            this.form = t.container.querySelector(kr),
            this.filtersInputs = [],
            this.form && (new Tr(this.form),
            this.filtersInputs = this.form.querySelectorAll(Ar),
            this.priceMin = this.form.querySelector(qr),
            this.priceMax = this.form.querySelector(xr),
            this.init())
        }
        init() {
            this.filtersInputs.length && this.filtersInputs.forEach((t=>{
                t.addEventListener("input", _((()=>{
                    this.form && "function" == typeof this.form.submit && (this.priceMin && t.hasAttribute(_r) && !this.priceMax.value && (this.priceMax.value = this.priceMax.placeholder),
                    this.priceMax && t.hasAttribute(Pr) && !this.priceMin.value && (this.priceMin.value = this.priceMin.placeholder),
                    this.form.submit())
                }
                ), 500))
            }
            )),
            this.form.addEventListener("range:filter:update", (()=>this.updateRange()))
        }
        updateRange() {
            if (this.form && "function" == typeof this.form.submit) {
                const t = this.form.querySelector(Cr)
                  , e = this.form.querySelector(Dr)
                  , i = this.form.querySelector(qr)
                  , s = this.form.querySelector(xr);
                if (t && e && i && s && t.hasAttribute(Mr) && e.hasAttribute(Hr)) {
                    const n = parseInt(i.placeholder)
                      , o = parseInt(s.placeholder)
                      , r = parseInt(t.getAttribute(Mr))
                      , a = parseInt(e.getAttribute(Hr));
                    n === r && o === a || (i.value = r,
                    s.value = a,
                    this.form.submit())
                }
            }
        }
    }
    const Br = {
        onLoad() {
            this.filterForm = new Ir(this)
        },
        onUnload: function() {
            this.filterForm && "function" == typeof this.filterForm.unload && this.filterForm.unload()
        }
    }
      , $r = "data-tooltip";
    let Fr = {};
    class Or {
        constructor(t) {
            this.tooltip = t,
            this.label = this.tooltip.getAttribute($r),
            this.pop = null,
            this.init()
        }
        init() {
            this.pop = new c({
                target: this.tooltip,
                popover: `\n        <div class="poppy__tooltip__wrapper">\n          <div class="poppy__tooltip">\n            ${this.label}\n          </div>\n        </div>\n      `,
                position: "top",
                transitionSpeed: 200
            }),
            this.tooltip.addEventListener("mouseenter", this.pop.pin),
            this.tooltip.addEventListener("mouseleave", this.pop.unpin)
        }
        unload() {
            this.tooltip.removeEventListener("mouseenter", this.pop.pin),
            this.tooltip.removeEventListener("mouseleave", this.pop.unpin)
        }
    }
    const Wr = {
        onLoad() {
            Fr[this.id] = [];
            this.container.querySelectorAll(`[${$r}]`).forEach((t=>{
                Fr[this.id].push(new Or(t))
            }
            ))
        },
        onUnload: function() {
            Fr[this.id].forEach((t=>{
                "function" == typeof t.unload && t.unload()
            }
            ))
        }
    }
      , jr = "[data-filters]"
      , Nr = "data-filters"
      , zr = "[data-filters-underlay]"
      , Vr = "data-default-hide"
      , Rr = "data-filters-toggle"
      , Ur = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      , Jr = "data-group-heading"
      , Kr = "data-show-more"
      , Xr = "data-swatch"
      , Yr = "drawer--visible"
      , Qr = "filters--default-visible"
      , Gr = "hidden"
      , Zr = "is-hidden"
      , ta = {};
    class ea {
        constructor(t) {
            this.container = t,
            this.underlay = this.container.querySelector(zr),
            this.groupHeadings = this.container.querySelectorAll(`[${Jr}]`),
            this.showMoreButtons = this.container.querySelectorAll(`[${Kr}]`),
            this.swatches = this.container.querySelectorAll(`[${Xr}]`);
            const e = this.container.getAttribute(Nr)
              , i = `[${Rr}='${e}']`;
            this.filtersToggleButtons = document.querySelectorAll(i),
            this.connectToggleMemory = t=>this.connectToggleFunction(t),
            this.connectShowHiddenOptions = t=>this.showHiddenOptions(t),
            this.connectToggle(),
            this.onFocusOut(),
            this.expandingEvents(),
            this.swatches && this.swatches.forEach((t=>{
                new ls(t)
            }
            )),
            this.getShowOnLoad() ? this.showFilters() : this.hideFilters()
        }
        unload() {
            this.filtersToggleButtons.length && this.filtersToggleButtons.forEach((t=>{
                t.removeEventListener("click", this.connectToggleMemory)
            }
            )),
            this.showMoreButtons.length && this.showMoreButtons.forEach((t=>{
                t.addEventListener("click", this.connectShowHiddenOptions)
            }
            ))
        }
        expandingEvents() {
            this.showMoreButtons.length && this.showMoreButtons.forEach((t=>{
                t.addEventListener("click", ((t,e)=>{
                    let i, s;
                    return function n(...o) {
                        const r = Date.now();
                        s = clearTimeout(s),
                        !i || r - i >= e ? (t.apply(null, o),
                        i = r) : s = setTimeout(n.bind(null, ...o), e - (r - i))
                    }
                }
                )(this.connectShowHiddenOptions, 500))
            }
            ))
        }
        showHiddenOptions(t) {
            const e = t.target.hasAttribute(Kr) ? t.target : t.target.closest(`[${Kr}]`);
            e.classList.add(Zr),
            e.previousElementSibling.querySelectorAll("." + Zr).forEach((t=>{
                t.classList.remove(Zr)
            }
            ))
        }
        connectToggle() {
            this.filtersToggleButtons.forEach((t=>{
                t.addEventListener("click", this.connectToggleMemory.bind(this))
            }
            ))
        }
        connectToggleFunction(t) {
            "true" === t.currentTarget.getAttribute("aria-expanded") ? this.hideFilters() : this.showFilters()
        }
        onFocusOut() {
            this.container.addEventListener("focusout", function(t) {
                if (window.innerWidth >= window.theme.sizes.medium)
                    return;
                const e = t.currentTarget.contains(t.relatedTarget)
                  , i = this.container.classList.contains(Yr);
                document.body.classList.contains("focus-enabled") && i && !e && this.hideFilters()
            }
            .bind(this)),
            this.container.addEventListener("keyup", function(t) {
                t.which === window.theme.keyboardKeys.ESCAPE && (this.hideFilters(),
                this.filtersToggleButtons[0].focus())
            }
            .bind(this)),
            this.underlay.addEventListener("click", function() {
                this.hideFilters()
            }
            .bind(this))
        }
        getShowOnLoad() {
            const t = `[${Vr}='false']`
              , e = document.querySelector(t)
              , i = window.innerWidth >= window.theme.sizes.medium;
            return !(!e || !i)
        }
        showFilters() {
            this.container.classList.remove(Gr),
            setTimeout((()=>{
                this.filtersToggleButtons.forEach((t=>t.setAttribute("aria-expanded", !0))),
                this.filtersToggleButtons.forEach((t=>t.classList.add(Yr))),
                this.container.classList.add(Yr),
                this.container.querySelector(Ur).focus()
            }
            ), 1)
        }
        hideFilters() {
            this.filtersToggleButtons.forEach((t=>t.setAttribute("aria-expanded", !1))),
            this.container.classList.remove(Yr),
            this.container.classList.remove(Qr),
            this.filtersToggleButtons.forEach((t=>t.classList.remove(Yr))),
            this.filtersToggleButtons.forEach((t=>t.classList.remove(Qr))),
            setTimeout((()=>{
                this.container.classList.contains(Yr) || this.container.classList.add(Gr)
            }
            ), 800)
        }
    }
    const ia = {
        onLoad() {
            ta[this.id] = [];
            this.container.querySelectorAll(jr).forEach((t=>{
                ta[this.id].push(new ea(t))
            }
            ))
        },
        onUnload: function() {
            ta[this.id].forEach((t=>{
                "function" == typeof t.unload && t.unload()
            }
            ))
        }
    };
    Pt("search-page", [lo, ia, Br, us, Wr, vn]);
    const sa = "[data-image-zoom]"
      , na = "data-unique";
    class oa {
        constructor(t) {
            this.triggers = t.querySelectorAll(sa),
            this.init()
        }
        init() {
            this.triggers.forEach((t=>{
                const i = t.getAttribute(na);
                e.init({
                    disableScroll: !0,
                    openTrigger: "data-popup-" + i,
                    onShow: t=>{
                        t.querySelectorAll("[data-src]", t).forEach((t=>{
                            if (null === t.getAttribute("src")) {
                                const e = t.getAttribute("data-src");
                                t.setAttribute("src", e)
                            }
                        }
                        ))
                    }
                    ,
                    onClose: (t,e,i)=>{
                        i.preventDefault()
                    }
                })
            }
            ))
        }
    }
    Pt("gallery", [{
        onLoad() {
            new oa(this.container)
        }
    }, Uo]);
    var ra = {}
      , aa = {}
      , la = {};
    const ca = "[data-product-slideshow]"
      , ha = "[data-shopify-xr]"
      , da = "data-media-id"
      , ua = "data-model-id"
      , pa = "model-viewer"
      , ma = "data-shopify-model3d-id"
      , ya = "#ModelJson-";
    function fa(t) {
        if (t)
            console.warn(t);
        else if (window.ShopifyXR) {
            for (const t in ra)
                if (ra.hasOwnProperty(t)) {
                    const e = ra[t];
                    if (e.loaded)
                        continue;
                    const i = document.querySelector(`${ya}${t}`);
                    i && (window.ShopifyXR.addModels(JSON.parse(i.innerHTML)),
                    e.loaded = !0)
                }
            window.ShopifyXR.setupXRElements()
        } else
            document.addEventListener("shopify_xr_initialized", (function() {
                fa()
            }
            ))
    }
    function ga(t) {
        if (t)
            console.warn(t);
        else
            for (const t in aa)
                if (aa.hasOwnProperty(t)) {
                    const e = aa[t];
                    e.modelViewerUi || (e.modelViewerUi = new Shopify.ModelViewerUI(e.$element)),
                    wa(e)
                }
    }
    function wa(t) {
        const e = la[t.sectionId];
        t.$container.addEventListener("pause", (function() {
            t.modelViewerUi.pause && t.modelViewerUi.pause()
        }
        )),
        t.$container.addEventListener("play-desktop", (function() {
            t.modelViewerUi.play && !Io() && t.modelViewerUi.play(),
            e && e.$element && t && t.modelId && ma && e.$element.setAttribute(ma, t.modelId)
        }
        )),
        t.$container.addEventListener("play", (function() {
            t.modelViewerUi.play && t.modelViewerUi.play()
        }
        ))
    }
    async function va(t) {
        const e = document.querySelector(`[data-player="${t}"]`)
          , i = e.querySelector("video");
        await Ki({
            name: "video-ui",
            version: "1.0"
        });
        const s = new window.Shopify.Plyr(i);
        return e.addEventListener("pause", (function() {
            s.pause && s.pause()
        }
        )),
        e.addEventListener("play-desktop", (function() {
            s.play && !Io() && e.dispatchEvent(new CustomEvent("play"))
        }
        )),
        e.addEventListener("play", (function() {
            try {
                s.play ? s.play() : s.addEventListener("onReady", (function(t) {
                    t.target.play()
                }
                ))
            } catch (t) {
                console.warn(t)
            }
        }
        )),
        e.addEventListener("destroy", (function() {
            try {
                s.destroy && s.destroy()
            } catch (t) {
                console.warn(t)
            }
        }
        )),
        s
    }
    var ba = {
        productSlideshow: "[data-product-slideshow]",
        productThumbs: "[data-product-thumbs]",
        thumbImage: "[data-slideshow-thumbnail]",
        productImage: "[data-product-image]",
        mediaSlide: "[data-media-slide]",
        dataMediaId: "data-media-id",
        mediaType: "data-type",
        videoPlayerExternal: '[data-type="external_video"]',
        videoPlayerNative: '[data-type="video"]',
        modelViewer: '[data-type="model"]',
        allPlayers: "[data-player]",
        xrButton: "[data-shopify-xr]",
        xrButtonId: "data-shopify-model3d-id",
        loopVideo: "data-enable-video-looping",
        flickitylockHeight: "flickity-lock-height",
        alignment: "data-thumbs-align"
    };
    class Sa {
        constructor(t) {
            this.section = t,
            this.container = t.container,
            this.slideshow = this.container.querySelector(ba.productSlideshow),
            this.thumbWrapper = this.container.querySelector(ba.productThumbs),
            this.thumbImages = this.container.querySelectorAll(ba.thumbImage),
            this.loopVideo = "true" === this.container.getAttribute(ba.loopVideo),
            this.centerAlign = "center" === this.container.getAttribute(ba.alignment),
            this.flkty = null,
            this.flktyThumbs = null,
            this.currentSlide = null,
            this.init()
        }
        init() {
            this.createSlider(),
            this.detectVideo(),
            this.detectYouTube(),
            this.detect3d()
        }
        createSlider() {
            if (!this.slideshow)
                return;
            const t = this;
            let e = {
                autoPlay: !1,
                prevNextButtons: !1,
                contain: !0,
                pageDots: !1,
                adaptiveHeight: !0,
                accessibility: !0,
                wrapAround: !0,
                fade: !0,
                on: {
                    ready: function() {
                        t.sliderThumbs()
                    }
                }
            };
            this.flkty = new l(this.slideshow,e),
            this.flkty.resize(),
            this.currentSlide = this.slideshow.querySelectorAll(ba.mediaSlide)[0],
            this.setDraggable(),
            this.flkty.on("change", function(t) {
                this.currentSlide.dispatchEvent(new CustomEvent("pause")),
                this.currentSlide = this.flkty.cells[t].element,
                this.slideshow.classList.remove(ba.flickitylockHeight)
            }
            .bind(this)),
            this.flkty.on("settle", function(t) {
                this.currentSlide = this.flkty.cells[t].element,
                this.setDraggable(),
                this.currentSlide.dispatchEvent(new CustomEvent("play-desktop"));
                document.body.classList.contains(ba.focusEnabled) && this.currentSlide.dispatchEvent(new Event("focus")),
                this.confirmSync()
            }
            .bind(this)),
            this.eventListeners()
        }
        eventListeners() {
            this.slideshow.addEventListener("theme:image:change", function(t) {
                var e = t.detail.id;
                const i = `[${ba.dataMediaId}="${e}"]`
                  , s = this.flkty.cells.findIndex((t=>t.element.matches(i)));
                this.flkty.select(s)
            }
            .bind(this)),
            this.thumbImages.forEach((t=>{
                t.addEventListener("click", function(t) {
                    const e = t.currentTarget.getAttribute("data-media-select");
                    this.slideshow.dispatchEvent(new CustomEvent("theme:image:change",{
                        detail: {
                            id: e
                        }
                    }))
                }
                .bind(this))
            }
            ))
        }
        sliderThumbs() {
            let t = {
                freeScroll: !0,
                contain: !0,
                prevNextButtons: !1,
                pageDots: !1,
                accessibility: !0,
                cellAlign: this.centerAlign ? "center" : "left",
                sync: this.slideshow
            };
            this.flktyThumbs = new d(this.thumbWrapper,t)
        }
        confirmSync() {
            this.flkty.selectedIndex !== this.flktyThumbs.selectedIndex && this.flkty.resize()
        }
        setDraggable() {
            if (this.currentSlide) {
                const t = this.currentSlide.getAttribute(ba.mediaType);
                "model" === t || "video" === t || "external_video" === t ? (this.flkty.options.draggable = !1,
                this.flkty.updateDraggable()) : (this.flkty.options.draggable = !0,
                this.flkty.updateDraggable())
            }
        }
        detect3d() {
            const t = this.container.querySelectorAll(ba.modelViewer);
            t && (t.forEach((t=>{
                !function(t, e) {
                    ra[e] = {
                        loaded: !1
                    };
                    const i = t.getAttribute(da)
                      , s = t.querySelector(pa)
                      , n = s.getAttribute(ua)
                      , o = t.closest(ca).parentElement.querySelector(ha);
                    la[e] = {
                        $element: o,
                        defaultId: n
                    },
                    aa[i] = {
                        modelId: n,
                        mediaId: i,
                        sectionId: e,
                        $container: t,
                        $element: s
                    },
                    window.Shopify.loadFeatures([{
                        name: "shopify-xr",
                        version: "1.0",
                        onLoad: fa
                    }, {
                        name: "model-viewer-ui",
                        version: "1.0",
                        onLoad: ga
                    }])
                }(t, this.section.id)
            }
            )),
            document.addEventListener("shopify_xr_launch", function() {
                this.container.querySelectorAll(ba.allPlayers).forEach((t=>{
                    t.dispatchEvent(new CustomEvent("pause"))
                }
                ))
            }
            .bind(this)))
        }
        detectVideo() {
            const t = this.section.container.querySelectorAll(ba.videoPlayerNative);
            for (var e of t) {
                const t = va(e.dataset.player);
                !0 === this.loopVideo && t.then((t=>(t.loop = !0,
                t))).catch((t=>{
                    console.error(t)
                }
                ))
            }
        }
        detectYouTube() {
            const t = this.section.container.querySelectorAll(ba.videoPlayerExternal);
            for (var e of t) {
                const t = $o(e.dataset.player);
                !0 === this.loopVideo && t.then((t=>Ea(t))).catch((t=>{
                    console.error(t)
                }
                ))
            }
        }
        pauseAllMedia() {
            this.container.querySelector("[data-media-slide]").dispatchEvent(new CustomEvent("pause"))
        }
        pauseOtherMedia(t) {
            this.container.querySelector(`[data-media-slide]:not([data-player="${t}"])`).dispatchEvent(new CustomEvent("pause"))
        }
        destroy() {
            this.container.querySelectorAll(ba.allPlayers).forEach((t=>{
                t.dispatchEvent(new CustomEvent("destroy"))
            }
            ))
        }
    }
    function Ea(t) {
        return t.addEventListener("onStateChange", (function(t) {
            0 === t.data && t.target.playVideo()
        }
        )),
        t
    }
    const La = "[data-store-availability-container]"
      , Ta = "[data-api-content]"
      , ka = "[data-pickup-drawer]"
      , Aa = "[data-pickup-drawer-open]"
      , qa = "[data-pickup-drawer-close]"
      , xa = "drawer--visible";
    let _a = {};
    class Pa {
        constructor(t) {
            this.container = t.container,
            this.drawer = null,
            this.buttonDrawerOpen = null,
            this.buttonDrawerClose = null,
            this.container.addEventListener("theme:variant:change", (t=>this.fetchPickupAvailability(t)))
        }
        fetchPickupAvailability(t) {
            const e = this.container.querySelector(La)
              , i = t.detail.variant;
            e && i && fetch(`${window.theme.routes.root_url}variants/${i.id}/?section_id=api-pickup-availability`).then((t=>t.text())).then((t=>{
                const i = (new DOMParser).parseFromString(t, "text/html").querySelector(Ta).innerHTML;
                e.innerHTML = i,
                this.drawer = this.container.querySelector(ka),
                this.buttonDrawerOpen = this.container.querySelector(Aa),
                this.buttonDrawerClose = this.container.querySelectorAll(qa),
                this.buttonDrawerOpen && this.buttonDrawerOpen.addEventListener("click", (()=>this.openDrawer())),
                this.buttonDrawerClose.length && this.buttonDrawerClose.forEach((t=>{
                    t.addEventListener("click", (()=>this.closeDrawer()))
                }
                ))
            }
            )).catch((t=>{
                console.error(t)
            }
            ))
        }
        openDrawer() {
            this.drawer && (this.drawer.classList.add(xa),
            this.drawer.dispatchEvent(new CustomEvent("theme:scroll:lock",{
                bubbles: !0
            })))
        }
        closeDrawer() {
            this.drawer && (this.drawer.classList.remove(xa),
            this.drawer.dispatchEvent(new CustomEvent("theme:scroll:unlock",{
                bubbles: !0
            })))
        }
    }
    const Ca = {
        onLoad() {
            _a[this.id] = new Pa(this)
        }
    }
      , Da = t=>{
        t && (t.style.display = "none")
    }
      , Ma = "[data-product-form]"
      , Ha = "[data-product-slideshow]"
      , Ia = "[data-add-to-cart]"
      , Ba = "[data-add-to-cart-text]"
      , $a = "[data-compare-price]"
      , Fa = "[data-compare-text]"
      , Oa = "[data-buttons-wrapper]"
      , Wa = "[data-product-select]"
      , ja = "[data-price-wrapper]"
      , Na = "[data-button-price]"
      , za = "[data-product-json]"
      , Va = "[data-product-price]"
      , Ra = "[data-product-unit-price]"
      , Ua = "[data-product-base]"
      , Ja = "[data-product-unit]"
      , Ka = "data-enable-history-state"
      , Xa = "data-option-position"
      , Ya = "[data-option-value]"
      , Qa = "[data-subscription-watch-price]"
      , Ga = "[data-subscription-selectors]"
      , Za = "[data-price-off]"
      , tl = "[data-price-off-type]"
      , el = "[data-price-off-amount]"
      , il = "[data-toggles-group]"
      , sl = "data-group-toggle"
      , nl = "[data-plan-description]"
      , ol = "[data-remaining-count]"
      , rl = "[data-remaining-max]"
      , al = "data-remaining-max"
      , ll = "[data-remaining-wrapper]"
      , cl = "[data-product-remaining-json]"
      , hl = "_preorder"
      , dl = "hide"
      , ul = "variant--soldout"
      , pl = "variant--unavailable"
      , ml = "product__price--sale"
      , yl = "variant__countdown--show";
    class fl {
        constructor(t) {
            if (this.section = t,
            this.container = t.container,
            this.productForm = this.container.querySelector(Ma),
            this.slideshow = this.container.querySelector(Ha),
            this.enableHistoryState = "true" === this.container.getAttribute(Ka),
            this.hasUnitPricing = this.container.querySelector(Ja),
            this.subSelectors = this.container.querySelector(Ga),
            this.subPrices = this.container.querySelector(Qa),
            this.priceOffWrap = this.container.querySelector(Za),
            this.priceOffAmount = this.container.querySelector(el),
            this.planDecription = this.container.querySelector(nl),
            this.priceOffType = this.container.querySelector(tl),
            this.remainingWrapper = this.container.querySelector(ll),
            this.remainingWrapper) {
                const t = this.container.querySelector(rl);
                this.remainingMaxInt = parseInt(t.getAttribute(al), 10),
                this.remainingCount = this.container.querySelector(ol),
                this.remainingJSONWrapper = this.container.querySelector(cl),
                this.remainingJSON = null,
                this.remainingJSONWrapper && "" !== this.remainingJSONWrapper.innerHTML ? this.remainingJSON = JSON.parse(this.remainingJSONWrapper.innerHTML) : console.warn("Missing product quantity JSON")
            }
            zs(this.container),
            this.init()
        }
        init() {
            let t = null;
            this.productJSON = null;
            const e = this.container.querySelector(za);
            e && (t = e.innerHTML),
            t && this.productForm ? (this.productJSON = JSON.parse(t),
            this.linkForm()) : console.warn("Missing product form or product JSON"),
            this.productJSON && new it(this.productJSON.handle)
        }
        destroy() {
            this.productForm.destroy()
        }
        linkForm() {
            this.productForm = new Ui(this.productForm,this.productJSON,{
                onOptionChange: this.onOptionChange.bind(this),
                onPlanChange: this.onPlanChange.bind(this),
                onQuantityChange: this.onQuantityChange.bind(this)
            }),
            this.pushState(this.productForm.getFormState()),
            this.subsToggleListeners()
        }
        onOptionChange(t) {
            this.pushState(t.dataset)
        }
        onPlanChange(t) {
            this.subPrices && this.pushState(t.dataset)
        }
        onQuantityChange(t) {
            const e = t.dataset;
            this.productState = this.setProductState(e),
            this.updateButtonPrices(e)
        }
        pushState(t) {
            this.productState = this.setProductState(t),
            this.updateProductImage(t),
            this.updateAddToCartState(t),
            this.updateProductPrices(t),
            this.updateSaleText(t),
            this.updateSubscriptionText(t),
            this.updateLegend(t),
            this.updateRemaining(t),
            this.fireHookEvent(t),
            this.enableHistoryState && this.updateHistoryState(t)
        }
        updateAddToCartState(t) {
            const e = t.variant;
            let i = theme.strings.addToCart;
            const s = this.container.querySelectorAll(ja)
              , n = this.container.querySelector(Oa)
              , o = n.querySelectorAll(Ia)
              , r = n.querySelectorAll(Ba);
            if (this.productJSON.tags.includes(hl) && (i = theme.strings.preOrder),
            s.length && e && s.forEach((t=>{
                t.classList.remove(dl)
            }
            )),
            o.length && o.forEach((t=>{
                e && e.available ? t.disabled = !1 : t.disabled = !0
            }
            )),
            r.length && r.forEach((t=>{
                e ? e.available ? t.innerHTML = i : t.innerHTML = theme.strings.soldOut : t.innerHTML = theme.strings.unavailable
            }
            )),
            n)
                if (e) {
                    e.available ? n.classList.remove(ul, pl) : (n.classList.add(ul),
                    n.classList.remove(pl));
                    const t = n.querySelector(Wa);
                    t && (t.value = e.id)
                } else
                    n.classList.add(pl),
                    n.classList.remove(ul)
        }
        updateLegend(t) {
            const e = t.variant;
            if (e) {
                this.container.querySelectorAll(Ya).forEach((t=>{
                    const i = t.closest(`[${Xa}]`);
                    if (i) {
                        const s = i.getAttribute(Xa)
                          , n = parseInt(s, 10) - 1
                          , o = e.options[n];
                        t.innerHTML = o
                    }
                }
                ))
            }
        }
        updateHistoryState(t) {
            const e = t.variant
              , i = t.plan
              , s = window.location.href;
            if (e && s.includes("/product")) {
                const t = new window.URL(s)
                  , n = t.searchParams;
                n.set("variant", e.id),
                i && i.detail && i.detail.id && this.productState.hasPlan ? n.set("selling_plan", i.detail.id) : n.delete("selling_plan"),
                t.search = n.toString();
                const o = t.toString();
                window.history.replaceState({
                    path: o
                }, "", o)
            }
        }
        updateRemaining(t) {
            const e = t.variant;
            if (e && this.remainingWrapper && this.remainingJSON && this.remainingCount) {
                const t = this.remainingJSON[e.id];
                t && t <= this.remainingMaxInt && t > 0 ? (this.remainingWrapper.classList.add(yl),
                this.remainingCount.innerHTML = t) : this.remainingWrapper.classList.remove(yl)
            } else
                this.remainingWrapper && this.remainingWrapper.classList.remove(yl)
        }
        getBaseUnit(t) {
            return 1 === t.unit_price_measurement.reference_value ? t.unit_price_measurement.reference_unit : t.unit_price_measurement.reference_value + t.unit_price_measurement.reference_unit
        }
        subsToggleListeners() {
            this.container.querySelectorAll(il).forEach((t=>{
                t.addEventListener("change", function(t) {
                    const e = t.target.value.toString()
                      , i = this.container.querySelector(`[${sl}="${e}"]`)
                      , s = this.container.querySelectorAll(`[${sl}]`);
                    if (i) {
                        i.classList.remove(dl);
                        const t = i.querySelector('[name="selling_plan"]');
                        t.checked = !0,
                        t.dispatchEvent(new Event("change"))
                    }
                    s.forEach((t=>{
                        if (t !== i) {
                            t.classList.add(dl);
                            t.querySelectorAll('[name="selling_plan"]').forEach((t=>{
                                t.checked = !1,
                                t.dispatchEvent(new Event("change"))
                            }
                            ))
                        }
                    }
                    ))
                }
                .bind(this))
            }
            ))
        }
        updateSaleText(t) {
            this.productState.planSale ? this.updateSaleTextSubscription(t) : this.productState.onSale ? this.updateSaleTextStandard(t) : this.priceOffWrap && this.priceOffWrap.classList.add(dl)
        }
        updateSaleTextStandard(t) {
            if (!this.priceOffType)
                return;
            this.priceOffType.innerHTML = window.theme.strings.sale || "sale";
            const e = t.variant;
            if (window.theme.settings.badge_sale_type && "percentage" === window.theme.settings.badge_sale_type) {
                const t = (e.compare_at_price - e.price) / e.compare_at_price
                  , i = Math.floor(100 * t);
                this.priceOffAmount.innerHTML = i + "%"
            } else {
                const t = e.compare_at_price - e.price;
                this.priceOffAmount.innerHTML = n.formatMoney(t, theme.moneyFormat)
            }
            this.priceOffWrap.classList.remove(dl)
        }
        updateSaleTextSubscription(t) {
            this.priceOffType.innerHTML = window.theme.strings.subscription || "subscripton";
            const e = t.plan.detail.price_adjustments[0]
              , i = e.value;
            e && "percentage" === e.value_type ? this.priceOffAmount.innerHTML = i + "%" : this.priceOffAmount.innerHTML = n.formatMoney(i, theme.moneyFormat),
            this.priceOffWrap.classList.remove(dl)
        }
        updateSubscriptionText(t) {
            t.plan && this.planDecription ? (this.planDecription.innerHTML = t.plan.detail.description,
            this.planDecription.classList.remove(dl)) : this.planDecription && this.planDecription.classList.add(dl)
        }
        getPrices(t) {
            const e = t.variant
              , i = t.plan;
            let s = ""
              , n = "";
            return this.productState.available && (s = e.compare_at_price,
            n = e.price),
            this.productState.hasPlan && (n = i.allocation.price),
            this.productState.planSale && (s = i.allocation.compare_at_price,
            n = i.allocation.price),
            {
                price: n,
                comparePrice: s
            }
        }
        updateButtonPrices(t) {
            const e = this.container.querySelectorAll(Na)
              , {price: i} = this.getPrices(t);
            e.length && e.forEach((e=>{
                const s = t.quantity * i;
                e.innerHTML = n.formatMoney(s, theme.moneyFormat)
            }
            ))
        }
        updateProductPrices(t) {
            const e = t.variant
              , i = this.container.querySelectorAll(ja)
              , s = this.container.querySelectorAll(Na)
              , {price: o, comparePrice: r} = this.getPrices(t);
            i.forEach((t=>{
                const i = t.querySelector($a)
                  , s = t.querySelector(Va)
                  , a = t.querySelector(Fa);
                i && (this.productState.onSale || this.productState.planSale ? (i.classList.remove(dl),
                a.classList.remove(dl),
                s.classList.add(ml)) : (i.classList.add(dl),
                a.classList.add(dl),
                s.classList.remove(ml)),
                i.innerHTML = n.formatMoney(r, theme.moneyFormat)),
                s && (s.innerHTML = e ? n.formatMoney(o, theme.moneyFormat) : "&nbsp;")
            }
            )),
            s.length && s.forEach((e=>{
                const i = t.quantity * o;
                e.innerHTML = n.formatMoney(i, theme.moneyFormat)
            }
            )),
            this.hasUnitPricing && this.updateProductUnits(t)
        }
        updateProductUnits(t) {
            const e = t.variant
              , i = t.plan;
            let s = null;
            if (e && e.unit_price && (s = e.unit_price),
            i && i.allocation && i.allocation.unit_price && (s = i.allocation.unit_price),
            s) {
                const t = this.getBaseUnit(e)
                  , i = n.formatMoney(s, theme.moneyFormat);
                this.container.querySelector(Ra).innerHTML = i,
                this.container.querySelector(Ua).innerHTML = t,
                F(this.container.querySelector(Ja))
            } else
                Da(this.container.querySelector(Ja))
        }
        fireHookEvent(t) {
            const e = t.variant;
            this.container.dispatchEvent(new CustomEvent("theme:variant:change",{
                detail: {
                    variant: e
                },
                bubbles: !0
            }))
        }
        setProductState(t) {
            const e = t.variant
              , i = t.plan
              , s = {
                available: !0,
                soldOut: !1,
                onSale: !1,
                showUnitPrice: !1,
                requiresPlan: !1,
                hasPlan: !1,
                planPerDelivery: !1,
                planSale: !1
            };
            return !e || e.requires_selling_plan && !i ? s.available = !1 : (e.available || (s.soldOut = !0),
            e.compare_at_price > e.price && (s.onSale = !0),
            e.unit_price && (s.showUnitPrice = !0),
            this.productJSON && this.productJSON.requires_selling_plan && (s.requiresPlan = !0),
            i && this.subPrices && (s.hasPlan = !0,
            i.allocation.per_delivery_price !== i.allocation.price && (s.planPerDelivery = !0),
            e.price > i.allocation.price && (s.planSale = !0))),
            s
        }
        updateProductImage(t) {
            const e = t.variant;
            this.slideshow && e && e.featured_media && e.featured_media.id && this.slideshow.dispatchEvent(new CustomEvent("theme:image:change",{
                detail: {
                    id: e.featured_media.id
                }
            }))
        }
    }
    const gl = {
        onLoad() {
            this.section = new fl(this)
        }
    }
      , wl = "[data-product-slideshow]"
      , vl = "[data-product-image]"
      , bl = "[data-zoom-button]"
      , Sl = "[data-zoom-wrapper]"
      , El = "[data-media-id]"
      , Ll = "data-media-id";
    const Tl = {
        scrollbar: "data-scrollbar-slider",
        scrollbarArrowPrev: "[data-scrollbar-arrow-prev]",
        scrollbarArrowNext: "[data-scrollbar-arrow-next]"
    }
      , kl = {
        hide: "is-hidden"
    }
      , Al = {
        delay: 200
    };
    class ql {
        constructor(t) {
            this.scrollbar = t,
            this.arrowNext = this.scrollbar.parentNode.querySelector(Tl.scrollbarArrowNext),
            this.arrowPrev = this.scrollbar.parentNode.querySelector(Tl.scrollbarArrowPrev),
            this.init(),
            this.resize(),
            this.scrollbar.hasAttribute(Tl.scrollbar) && this.scrollToVisibleElement()
        }
        init() {
            this.arrowNext && this.arrowPrev && (this.toggleNextArrow(),
            this.events())
        }
        resize() {
            document.addEventListener("theme:resize", (()=>{
                this.toggleNextArrow()
            }
            ))
        }
        events() {
            this.arrowNext.addEventListener("click", (t=>{
                t.preventDefault(),
                this.goToNext()
            }
            )),
            this.arrowPrev.addEventListener("click", (t=>{
                t.preventDefault(),
                this.goToPrev()
            }
            )),
            this.scrollbar.addEventListener("scroll", (()=>{
                this.togglePrevArrow(),
                this.toggleNextArrow()
            }
            ))
        }
        goToNext() {
            const t = this.scrollbar.getBoundingClientRect().width / 2 + this.scrollbar.scrollLeft;
            this.move(t),
            this.arrowPrev.classList.remove(kl.hide),
            this.toggleNextArrow()
        }
        goToPrev() {
            const t = this.scrollbar.scrollLeft - this.scrollbar.getBoundingClientRect().width / 2;
            this.move(t),
            this.arrowNext.classList.remove(kl.hide),
            this.togglePrevArrow()
        }
        toggleNextArrow() {
            setTimeout((()=>{
                this.arrowNext.classList.toggle(kl.hide, Math.round(this.scrollbar.scrollLeft + this.scrollbar.getBoundingClientRect().width + 1) >= this.scrollbar.scrollWidth)
            }
            ), Al.delay)
        }
        togglePrevArrow() {
            setTimeout((()=>{
                this.arrowPrev.classList.toggle(kl.hide, this.scrollbar.scrollLeft <= 0)
            }
            ), Al.delay)
        }
        scrollToVisibleElement() {
            [].forEach.call(this.scrollbar.children, (t=>{
                t.addEventListener("click", (e=>{
                    e.preventDefault(),
                    this.move(t.offsetLeft - t.clientWidth)
                }
                ))
            }
            ))
        }
        move(t) {
            this.scrollbar.scrollTo({
                top: 0,
                left: t,
                behavior: "smooth"
            })
        }
    }
    const xl = "body"
      , _l = "[data-related-section]"
      , Pl = "[data-tabs-holder]"
      , Cl = "data-tab"
      , Dl = "data-tab-index"
      , Ml = "data-block-id"
      , Hl = "ul.tabs > li"
      , Il = ".tab-link"
      , Bl = ".tab-link__recent"
      , $l = ".tab-content"
      , Fl = "[data-scrollbar]"
      , Ol = "current"
      , Wl = "hide"
      , jl = "alt"
      , Nl = {};
    class zl {
        constructor(t) {
            this.container = t,
            this.body = document.querySelector(xl),
            this.accessibility = window.accessibility,
            this.container && (this.scrollbarHolder = this.container.querySelectorAll(Fl),
            this.init(),
            this.initNativeScrollbar())
        }
        init() {
            const t = this.container
              , e = t.querySelectorAll(Hl)
              , i = t.querySelector(Il + "-0")
              , s = t.querySelector($l + "-0");
            s && s.classList.add(Ol),
            i && i.classList.add(Ol),
            this.checkVisibleTabLinks(),
            this.container.addEventListener("tabs:checkRecentTab", (()=>this.checkRecentTab())),
            this.container.addEventListener("tabs:hideRelatedTab", (()=>this.hideRelatedTab())),
            e.length && e.forEach((e=>{
                const i = parseInt(e.getAttribute(Cl))
                  , s = t.querySelector(`${$l}-${i}`);
                e.addEventListener("click", (()=>{
                    this.tabChange(e, s)
                }
                )),
                e.addEventListener("keyup", (t=>{
                    t.which !== window.theme.keyboardKeys.SPACE && t.which !== window.theme.keyboardKeys.ENTER || !this.body.classList.contains("is-focused") || (this.tabChange(e, s),
                    s.querySelector("a, input") && (this.accessibility.lastFocused = e,
                    this.accessibility.a11y.trapFocus(s, {
                        elementToFocus: s.querySelector("a:first-child, input:first-child")
                    })))
                }
                ))
            }
            ))
        }
        tabChange(t, e) {
            this.container.querySelector(`${Hl}.${Ol}`).classList.remove(Ol),
            this.container.querySelector(`${$l}.${Ol}`).classList.remove(Ol),
            t.classList.add(Ol),
            e.classList.add(Ol),
            t.classList.contains(Wl) && e.classList.add(Wl),
            this.checkVisibleTabLinks(),
            this.container.dispatchEvent(new CustomEvent("theme:tab:change"))
        }
        initNativeScrollbar() {
            this.scrollbarHolder.length && this.scrollbarHolder.forEach((t=>{
                new ql(t)
            }
            ))
        }
        checkVisibleTabLinks() {
            const t = this.container.querySelectorAll(Hl)
              , e = this.container.querySelectorAll(`${Il}.${Wl}`);
            t.length - e.length < 2 ? this.container.classList.add(jl) : this.container.classList.remove(jl)
        }
        checkRecentTab() {
            const t = this.container.querySelector(Bl);
            if (t) {
                t.classList.remove(Wl);
                const e = parseInt(t.getAttribute(Cl))
                  , i = this.container.querySelector(`${$l}[${Dl}="${e}"]`);
                i && i.classList.remove(Wl),
                this.checkVisibleTabLinks(),
                this.initNativeScrollbar()
            }
        }
        hideRelatedTab() {
            const t = this.container.querySelector(_l);
            if (!t)
                return;
            const e = t.closest(`${$l}.${Ol}`);
            if (!e)
                return;
            const i = parseInt(e.getAttribute(Dl))
              , s = this.container.querySelectorAll(Hl);
            if (s.length > i) {
                const t = s[i].nextSibling;
                t && (s[i].classList.add(Wl),
                t.dispatchEvent(new Event("click")),
                this.initNativeScrollbar())
            }
        }
        onBlockSelect(t) {
            const e = this.container.querySelector(`${Il}[${Ml}="${t.detail.blockId}"]`);
            e && (e.dispatchEvent(new Event("click")),
            e.parentNode.scrollTo({
                top: 0,
                left: e.offsetLeft - e.clientWidth,
                behavior: "smooth"
            }))
        }
    }
    const Vl = {
        onLoad() {
            Nl[this.id] = [];
            this.container.querySelectorAll(Pl).forEach((t=>{
                Nl[this.id].push(new zl(t))
            }
            ))
        },
        onBlockSelect(t) {
            Nl[this.id].forEach((e=>{
                "function" == typeof e.onBlockSelect && e.onBlockSelect(t)
            }
            ))
        }
    }
      , Rl = "[data-product-form]"
      , Ul = "[data-product-json]"
      , Jl = "[data-zoom-button]"
      , Kl = "[data-truncated-holder]"
      , Xl = "[data-truncated-button]"
      , Yl = "[data-truncated-content]"
      , Ql = "data-truncated-content"
      , Gl = "is-expanded"
      , Zl = "is-visible"
      , tc = [];
    class ec {
        constructor(t) {
            this.section = t,
            this.id = t.id,
            this.container = t.container,
            this.settings = t.settings,
            this.productFormElement = this.container.querySelector(Rl),
            zt(this.id),
            this.media = new Sa(t);
            const e = this.container.querySelector(Ul);
            e && "" !== e.innerHTML ? (this.product = JSON.parse(e.innerHTML),
            this.truncateElementHolder = this.container.querySelector(Kl),
            this.truncateElement = this.container.querySelector(Yl),
            this.resizeEventTruncate = ()=>this.truncateText(),
            this.init()) : console.error("Missing product JSON")
        }
        init() {
            var t, e;
            this.zoomEnabled = null !== this.container.querySelector(Jl),
            this.zoomEnabled && (t = this.container,
            e = this.product,
            Ki({
                url: window.theme.assets.photoswipe
            }).then((()=>{
                const i = window.themePhotoswipe.PhotoSwipe.default
                  , s = window.themePhotoswipe.PhotoSwipeUI.default;
                t.querySelectorAll(bl).forEach((n=>{
                    n.addEventListener("click", (n=>{
                        const o = t.querySelector(Sl)
                          , r = n.target.closest(El).getAttribute(Ll).toString()
                          , a = [];
                        for (let t = 0; t < e.media.length; t++)
                            "image" === e.media[t].media_type && (a[a.length] = {
                                src: e.media[t].src,
                                w: e.media[t].width,
                                h: e.media[t].height,
                                id: e.media[t].id
                            });
                        const l = {
                            index: a.findIndex((t=>t.id.toString() === r)),
                            showHideOpacity: !0,
                            showAnimationDuration: 150,
                            hideAnimationDuration: 250,
                            bgOpacity: 1,
                            spacing: 0,
                            allowPanToNext: !1,
                            maxSpreadZoom: 3,
                            history: !1,
                            loop: !0,
                            pinchToClose: !1,
                            modal: !1,
                            closeOnScroll: !1,
                            closeOnVerticalDrag: !0,
                            getDoubleTapZoom: function(t, e) {
                                return t ? 1.67 : e.initialZoomLevel < .7 ? 1 : 1.3
                            },
                            getThumbBoundsFn: function() {
                                let e = t.querySelector(wl);
                                e || (e = t.querySelector(vl));
                                const i = window.pageYOffset || document.documentElement.scrollTop
                                  , s = e.getBoundingClientRect();
                                return {
                                    x: s.left,
                                    y: s.top + i,
                                    w: s.width
                                }
                            }
                        };
                        o.dispatchEvent(new CustomEvent("theme:scroll:lock",{
                            bubbles: !0
                        }));
                        const c = new i(o,s,a,l);
                        c.init(),
                        c.listen("close", (function() {
                            document.dispatchEvent(new CustomEvent("theme:scroll:unlock",{
                                bubbles: !0
                            }))
                        }
                        ))
                    }
                    ))
                }
                ))
            }
            )).catch((t=>console.error(t)))),
            this.truncateElementHolder && this.truncateElement && (setTimeout(this.resizeEventTruncate, 50),
            document.addEventListener("theme:resize", this.resizeEventTruncate))
        }
        truncateText() {
            if (this.truncateElementHolder.classList.contains(Zl))
                return;
            const t = this.truncateElement.cloneNode(!0)
              , e = this.truncateElement.getAttribute(Ql)
              , i = this.truncateElement.nextElementSibling;
            i && i.remove(),
            this.truncateElement.parentElement.append(t);
            const s = this.truncateElement.nextElementSibling;
            s.classList.add(e),
            s.removeAttribute(Ql),
            F(s),
            h.ellipsis(s, 5, {
                replaceStr: ""
            }),
            Da(s),
            this.truncateElement.innerHTML !== s.innerHTML ? this.truncateElementHolder.classList.add(Gl) : (s.remove(),
            this.truncateElementHolder.classList.remove(Gl)),
            this.toggleTruncatedContent(this.truncateElementHolder)
        }
        toggleTruncatedContent(t) {
            const e = t.querySelector(Xl);
            e && e.addEventListener("click", (e=>{
                e.preventDefault(),
                t.classList.remove(Gl),
                t.classList.add(Zl)
            }
            ))
        }
        onBlockSelect(t) {
            const e = this.container.querySelector(`[data-block-id="${t.detail.blockId}"]`);
            e && e.dispatchEvent(new Event("click"))
        }
        onBlockDeselect(t) {
            const e = this.container.querySelector(`[data-block-id="${t.detail.blockId}"]`);
            e && e.dispatchEvent(new Event("click"))
        }
        onUnload() {
            this.media.destroy(),
            this.truncateElementHolder && this.truncateElement && document.removeEventListener("theme:resize", this.resizeEventTruncate)
        }
    }
    Pt("product", [{
        onLoad() {
            tc[this.id] = new ec(this)
        },
        onUnload() {
            "function" == typeof tc[this.id].unload && tc[this.id].unload()
        },
        onBlockSelect(t) {
            "function" == typeof tc[this.id].onBlockSelect && tc[this.id].onBlockSelect(t)
        },
        onBlockDeselect(t) {
            "function" == typeof tc[this.id].onBlockDeselect && tc[this.id].onBlockDeselect(t)
        }
    }, Ca, gl, ds, Wr, $s, vn, Vl]);
    const ic = "data-toggle-grid"
      , sc = "data-grid-large"
      , nc = "data-grid-small"
      , oc = window.theme.sizes.small;
    var rc = {};
    class ac {
        constructor(t) {
            this.toggle = t,
            this.value = this.toggle.getAttribute(ic),
            this.toggleClickFunction = t=>this.toggleClick(t),
            this.init()
        }
        init() {
            this.toggle.addEventListener("click", this.toggleClickFunction)
        }
        unload() {
            this.toggle.removeEventListener("click", this.toggleClickFunction)
        }
        toggleClick() {
            const t = window.innerWidth >= oc ? sc : nc;
            document.querySelector(`[${t}]`).setAttribute(t, this.value),
            window.lazySizes && window.lazySizes.autoSizer.checkElems()
        }
    }
    const lc = {
        onLoad() {
            rc[this.id] = [];
            this.container.querySelectorAll(`[${ic}]`).forEach((t=>{
                rc[this.id].push(new ac(t))
            }
            ))
        },
        onUnload: function() {
            rc[this.id].forEach((t=>{
                "function" == typeof t.unload && t.unload()
            }
            ))
        }
    };
    var cc = "[data-sort-enabled]"
      , hc = "[data-sort-link]"
      , dc = "data-value"
      , uc = "[data-tag-group]"
      , pc = ".link--add"
      , mc = ".link--remove";
    class yc {
        constructor(t) {
            this.container = t.container,
            this.sort = this.container.querySelector(cc),
            this.sortLinks = this.container.querySelectorAll(hc),
            this.init()
        }
        init() {
            this.sort && this.initClick(),
            this.removeUnusableFilters()
        }
        removeUnusableFilters() {
            const t = this.container.querySelectorAll(uc);
            t.length > 0 && t.forEach((t=>{
                const e = t.querySelector(pc)
                  , i = t.querySelector(mc);
                e || i || Da(t)
            }
            ))
        }
        onClick(t) {
            const e = t.currentTarget.getAttribute(dc)
              , i = new window.URL(window.location.href)
              , s = i.searchParams;
            s.set("sort_by", e),
            i.search = s.toString(),
            window.location.replace(i.toString())
        }
        initClick() {
            this.sortLinks.forEach((t=>{
                t.addEventListener("click", function(t) {
                    this.onClick(t)
                }
                .bind(this))
            }
            ))
        }
    }
    Pt("collection", [{
        onLoad() {
            this.collection = new yc(this)
        }
    }, lo, ia, Br, lc, us, Wr, vn]),
    Pt("collection-row", us),
    Pt("collection-tabs", [Vl, er, us]);
    var fc = {};
    function gc(t) {
        return fc[t]
    }
    fc.basic = [],
    fc.light = [{
        featureType: "administrative",
        elementType: "labels",
        stylers: [{
            visibility: "on"
        }, {
            lightness: "64"
        }, {
            hue: "#ff0000"
        }]
    }, {
        featureType: "administrative",
        elementType: "labels.text.fill",
        stylers: [{
            color: "#bdbdbd"
        }]
    }, {
        featureType: "administrative",
        elementType: "labels.icon",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "landscape",
        elementType: "all",
        stylers: [{
            color: "#f0f0f0"
        }, {
            visibility: "simplified"
        }]
    }, {
        featureType: "landscape.natural.landcover",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "landscape.natural.terrain",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "poi",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "poi",
        elementType: "geometry.fill",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "poi",
        elementType: "labels",
        stylers: [{
            lightness: "100"
        }]
    }, {
        featureType: "poi.park",
        elementType: "all",
        stylers: [{
            visibility: "on"
        }]
    }, {
        featureType: "poi.park",
        elementType: "geometry",
        stylers: [{
            saturation: "-41"
        }, {
            color: "#e8ede7"
        }]
    }, {
        featureType: "poi.park",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "road",
        elementType: "all",
        stylers: [{
            saturation: "-100"
        }]
    }, {
        featureType: "road",
        elementType: "labels",
        stylers: [{
            lightness: "25"
        }, {
            gamma: "1.06"
        }, {
            saturation: "-100"
        }]
    }, {
        featureType: "road.highway",
        elementType: "all",
        stylers: [{
            visibility: "simplified"
        }]
    }, {
        featureType: "road.highway",
        elementType: "geometry.fill",
        stylers: [{
            gamma: "10.00"
        }]
    }, {
        featureType: "road.highway",
        elementType: "geometry.stroke",
        stylers: [{
            weight: "0.01"
        }, {
            visibility: "simplified"
        }]
    }, {
        featureType: "road.highway",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "road.highway",
        elementType: "labels.text.fill",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "road.highway",
        elementType: "labels.text.stroke",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "road.arterial",
        elementType: "geometry.fill",
        stylers: [{
            weight: "0.8"
        }]
    }, {
        featureType: "road.arterial",
        elementType: "geometry.stroke",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "road.arterial",
        elementType: "labels.icon",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "road.local",
        elementType: "geometry.fill",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "road.local",
        elementType: "geometry.stroke",
        stylers: [{
            gamma: "10.00"
        }, {
            lightness: "100"
        }, {
            weight: "0.4"
        }]
    }, {
        featureType: "road.local",
        elementType: "labels",
        stylers: [{
            visibility: "simplified"
        }, {
            weight: "0.01"
        }, {
            lightness: "39"
        }]
    }, {
        featureType: "road.local",
        elementType: "labels.text.stroke",
        stylers: [{
            weight: "0.50"
        }, {
            gamma: "10.00"
        }, {
            lightness: "100"
        }]
    }, {
        featureType: "transit",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "water",
        elementType: "all",
        stylers: [{
            color: "#cfe5ee"
        }, {
            visibility: "on"
        }]
    }],
    fc.light_blank = [{
        featureType: "all",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "administrative",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }, {
            lightness: "64"
        }, {
            hue: "#ff0000"
        }]
    }, {
        featureType: "administrative",
        elementType: "labels.text.fill",
        stylers: [{
            color: "#bdbdbd"
        }]
    }, {
        featureType: "administrative",
        elementType: "labels.icon",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "landscape",
        elementType: "all",
        stylers: [{
            color: "#f0f0f0"
        }, {
            visibility: "simplified"
        }]
    }, {
        featureType: "landscape.natural.landcover",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "landscape.natural.terrain",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "poi",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "poi",
        elementType: "geometry.fill",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "poi",
        elementType: "labels",
        stylers: [{
            lightness: "100"
        }]
    }, {
        featureType: "poi.park",
        elementType: "all",
        stylers: [{
            visibility: "on"
        }]
    }, {
        featureType: "poi.park",
        elementType: "geometry",
        stylers: [{
            saturation: "-41"
        }, {
            color: "#e8ede7"
        }]
    }, {
        featureType: "poi.park",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "road",
        elementType: "all",
        stylers: [{
            saturation: "-100"
        }]
    }, {
        featureType: "road",
        elementType: "labels",
        stylers: [{
            lightness: "25"
        }, {
            gamma: "1.06"
        }, {
            saturation: "-100"
        }, {
            visibility: "off"
        }]
    }, {
        featureType: "road.highway",
        elementType: "all",
        stylers: [{
            visibility: "simplified"
        }]
    }, {
        featureType: "road.highway",
        elementType: "geometry.fill",
        stylers: [{
            gamma: "10.00"
        }]
    }, {
        featureType: "road.highway",
        elementType: "geometry.stroke",
        stylers: [{
            weight: "0.01"
        }, {
            visibility: "simplified"
        }]
    }, {
        featureType: "road.highway",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "road.highway",
        elementType: "labels.text.fill",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "road.highway",
        elementType: "labels.text.stroke",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "road.arterial",
        elementType: "geometry.fill",
        stylers: [{
            weight: "0.8"
        }]
    }, {
        featureType: "road.arterial",
        elementType: "geometry.stroke",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "road.arterial",
        elementType: "labels.icon",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "road.local",
        elementType: "geometry.fill",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "road.local",
        elementType: "geometry.stroke",
        stylers: [{
            gamma: "10.00"
        }, {
            lightness: "100"
        }, {
            weight: "0.4"
        }]
    }, {
        featureType: "road.local",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }, {
            weight: "0.01"
        }, {
            lightness: "39"
        }]
    }, {
        featureType: "road.local",
        elementType: "labels.text.stroke",
        stylers: [{
            weight: "0.50"
        }, {
            gamma: "10.00"
        }, {
            lightness: "100"
        }]
    }, {
        featureType: "transit",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "water",
        elementType: "all",
        stylers: [{
            color: "#cfe5ee"
        }, {
            visibility: "on"
        }]
    }],
    fc.white_blank = [{
        featureType: "all",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "administrative",
        elementType: "labels.text.fill",
        stylers: [{
            color: "#444444"
        }]
    }, {
        featureType: "landscape",
        elementType: "all",
        stylers: [{
            color: "#f2f2f2"
        }]
    }, {
        featureType: "poi",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "road",
        elementType: "all",
        stylers: [{
            saturation: -100
        }, {
            lightness: 45
        }]
    }, {
        featureType: "road.highway",
        elementType: "all",
        stylers: [{
            visibility: "simplified"
        }]
    }, {
        featureType: "road.highway",
        elementType: "geometry.fill",
        stylers: [{
            weight: "0.8"
        }]
    }, {
        featureType: "road.highway",
        elementType: "geometry.stroke",
        stylers: [{
            weight: "0.8"
        }]
    }, {
        featureType: "road.highway",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "road.highway",
        elementType: "labels.text.fill",
        stylers: [{
            weight: "0.8"
        }]
    }, {
        featureType: "road.highway",
        elementType: "labels.text.stroke",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "road.arterial",
        elementType: "geometry.stroke",
        stylers: [{
            weight: "0"
        }]
    }, {
        featureType: "road.arterial",
        elementType: "labels.icon",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "road.local",
        elementType: "geometry.stroke",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "transit",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "water",
        elementType: "all",
        stylers: [{
            color: "#e4e4e4"
        }, {
            visibility: "on"
        }]
    }],
    fc.white_label = [{
        featureType: "all",
        elementType: "all",
        stylers: [{
            visibility: "simplified"
        }]
    }, {
        featureType: "all",
        elementType: "labels",
        stylers: [{
            visibility: "simplified"
        }]
    }, {
        featureType: "administrative",
        elementType: "labels",
        stylers: [{
            gamma: "3.86"
        }, {
            lightness: "100"
        }]
    }, {
        featureType: "administrative",
        elementType: "labels.text.fill",
        stylers: [{
            color: "#cccccc"
        }]
    }, {
        featureType: "landscape",
        elementType: "all",
        stylers: [{
            color: "#f2f2f2"
        }]
    }, {
        featureType: "poi",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "road",
        elementType: "all",
        stylers: [{
            saturation: -100
        }, {
            lightness: 45
        }]
    }, {
        featureType: "road.highway",
        elementType: "all",
        stylers: [{
            visibility: "simplified"
        }]
    }, {
        featureType: "road.highway",
        elementType: "geometry.fill",
        stylers: [{
            weight: "0.8"
        }]
    }, {
        featureType: "road.highway",
        elementType: "geometry.stroke",
        stylers: [{
            weight: "0.8"
        }]
    }, {
        featureType: "road.highway",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "road.highway",
        elementType: "labels.text.fill",
        stylers: [{
            weight: "0.8"
        }]
    }, {
        featureType: "road.highway",
        elementType: "labels.text.stroke",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "road.arterial",
        elementType: "geometry.stroke",
        stylers: [{
            weight: "0"
        }]
    }, {
        featureType: "road.arterial",
        elementType: "labels.icon",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "road.local",
        elementType: "geometry.stroke",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "road.local",
        elementType: "labels.text",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "transit",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "water",
        elementType: "all",
        stylers: [{
            color: "#e4e4e4"
        }, {
            visibility: "on"
        }]
    }],
    fc.dark_blank = [{
        featureType: "all",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "all",
        elementType: "labels.text.fill",
        stylers: [{
            saturation: 36
        }, {
            color: "#000000"
        }, {
            lightness: 40
        }]
    }, {
        featureType: "all",
        elementType: "labels.text.stroke",
        stylers: [{
            visibility: "on"
        }, {
            color: "#000000"
        }, {
            lightness: 16
        }]
    }, {
        featureType: "all",
        elementType: "labels.icon",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "administrative",
        elementType: "geometry.fill",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 20
        }]
    }, {
        featureType: "administrative",
        elementType: "geometry.stroke",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 17
        }, {
            weight: 1.2
        }]
    }, {
        featureType: "administrative",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "landscape",
        elementType: "geometry",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 20
        }]
    }, {
        featureType: "landscape",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "poi",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "poi",
        elementType: "geometry",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 21
        }]
    }, {
        featureType: "road",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "road.highway",
        elementType: "geometry.fill",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 17
        }, {
            weight: "0.8"
        }]
    }, {
        featureType: "road.highway",
        elementType: "geometry.stroke",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 29
        }, {
            weight: "0.01"
        }]
    }, {
        featureType: "road.arterial",
        elementType: "geometry",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 18
        }]
    }, {
        featureType: "road.arterial",
        elementType: "geometry.stroke",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "road.local",
        elementType: "geometry",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 16
        }]
    }, {
        featureType: "road.local",
        elementType: "geometry.stroke",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "transit",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "transit",
        elementType: "geometry",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 19
        }]
    }, {
        featureType: "water",
        elementType: "geometry",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 17
        }]
    }],
    fc.dark_label = [{
        featureType: "all",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "all",
        elementType: "labels.text.fill",
        stylers: [{
            saturation: 36
        }, {
            color: "#000000"
        }, {
            lightness: 40
        }]
    }, {
        featureType: "all",
        elementType: "labels.text.stroke",
        stylers: [{
            visibility: "on"
        }, {
            color: "#000000"
        }, {
            lightness: 16
        }]
    }, {
        featureType: "all",
        elementType: "labels.icon",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "administrative",
        elementType: "geometry.fill",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 20
        }]
    }, {
        featureType: "administrative",
        elementType: "geometry.stroke",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 17
        }, {
            weight: 1.2
        }]
    }, {
        featureType: "administrative",
        elementType: "labels",
        stylers: [{
            visibility: "simplified"
        }, {
            lightness: "-82"
        }]
    }, {
        featureType: "administrative",
        elementType: "labels.text.stroke",
        stylers: [{
            invert_lightness: !0
        }, {
            weight: "7.15"
        }]
    }, {
        featureType: "landscape",
        elementType: "geometry",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 20
        }]
    }, {
        featureType: "landscape",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "poi",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "poi",
        elementType: "geometry",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 21
        }]
    }, {
        featureType: "road",
        elementType: "labels",
        stylers: [{
            visibility: "simplified"
        }]
    }, {
        featureType: "road.highway",
        elementType: "geometry.fill",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 17
        }, {
            weight: "0.8"
        }]
    }, {
        featureType: "road.highway",
        elementType: "geometry.stroke",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 29
        }, {
            weight: "0.01"
        }]
    }, {
        featureType: "road.highway",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "road.arterial",
        elementType: "geometry",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 18
        }]
    }, {
        featureType: "road.arterial",
        elementType: "geometry.stroke",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "road.local",
        elementType: "geometry",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 16
        }]
    }, {
        featureType: "road.local",
        elementType: "geometry.stroke",
        stylers: [{
            weight: "0.01"
        }]
    }, {
        featureType: "road.local",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "transit",
        elementType: "all",
        stylers: [{
            visibility: "off"
        }]
    }, {
        featureType: "transit",
        elementType: "geometry",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 19
        }]
    }, {
        featureType: "water",
        elementType: "geometry",
        stylers: [{
            color: "#000000"
        }, {
            lightness: 17
        }]
    }],
    window.theme.allMaps = window.theme.allMaps || {};
    let wc = window.theme.allMaps;
    class vc {
        constructor(t) {
            this.container = t.container,
            this.mapWrap = this.container.querySelector("[data-map-container]"),
            this.styleString = this.container.getAttribute("data-style") || "",
            this.key = this.container.getAttribute("data-api-key"),
            this.zoomString = this.container.getAttribute("data-zoom") || 14,
            this.address = this.container.getAttribute("data-address"),
            this.enableCorrection = this.container.getAttribute("data-latlong-correction"),
            this.lat = this.container.getAttribute("data-lat"),
            this.long = this.container.getAttribute("data-long"),
            this.key && this.initMaps()
        }
        initMaps() {
            Ki({
                url: "https://maps.googleapis.com/maps/api/js?key=" + this.key
            }).then((()=>{
                return "true" === this.enableCorrection && "" !== this.lat && "" !== this.long ? new window.google.maps.LatLng(this.lat,this.long) : (t = this.address,
                new Promise(((e,i)=>{
                    (new window.google.maps.Geocoder).geocode({
                        address: t
                    }, (function(t, s) {
                        if ("OK" == s) {
                            var n = {
                                lat: t[0].geometry.location.lat(),
                                lng: t[0].geometry.location.lng()
                            };
                            e(n)
                        } else
                            i(s)
                    }
                    ))
                }
                )));
                var t
            }
            )).then((t=>{
                var e = {
                    zoom: parseInt(this.zoomString, 10),
                    styles: gc(this.styleString),
                    center: t,
                    draggable: !0,
                    clickableIcons: !1,
                    scrollwheel: !1,
                    zoomControl: !1,
                    disableDefaultUI: !0
                };
                return function(t, e) {
                    var i = new window.google.maps.Map(t,e)
                      , s = i.getCenter();
                    return new window.google.maps.Marker({
                        map: i,
                        position: s
                    }),
                    window.google.maps.event.addDomListener(window, "resize", (function() {
                        window.google.maps.event.trigger(i, "resize"),
                        i.setCenter(s)
                    }
                    )),
                    i
                }(this.mapWrap, e)
            }
            )).then((t=>{
                this.map = t,
                wc[this.id] = t
            }
            )).catch((t=>{
                console.log("Failed to load Google Map"),
                console.log(t)
            }
            ))
        }
        onUnload() {
            void 0 !== window.google && window.google.maps.event.clearListeners(this.map, "resize")
        }
    }
    Pt("section-map", {
        onLoad() {
            wc[this.id] = new vc(this)
        },
        onUnload() {
            "function" == typeof wc[this.id].unload && wc[this.id].unload()
        }
    }),
    Pt("section-columns", Uo);
    const bc = "[data-related-section]"
      , Sc = "[data-grid-item]"
      , Ec = "data-minimum"
      , Lc = "[data-recent-wrapper]"
      , Tc = "[data-recently-viewed-wrapper]"
      , kc = "[data-slider]";
    class Ac {
        constructor(t) {
            this.section = t,
            this.sectionId = t.id,
            this.container = t.container,
            this.init(),
            this.container.addEventListener("recent-products:added", (()=>{
                this.recent()
            }
            ))
        }
        init() {
            const t = this.container.querySelector(bc);
            if (!t)
                return;
            const e = t.getAttribute("data-product-id")
              , i = t.getAttribute("data-limit")
              , s = `${window.theme.routes.product_recommendations_url || "/recommendations/products/"}?section_id=related&limit=${i}&product_id=${e}`;
            a.get(s).then((function(e) {
                const i = document.createElement("div");
                i.innerHTML = e.data;
                const s = i.querySelector(bc);
                if (s.querySelector(Sc)) {
                    const e = s.innerHTML;
                    Da(t),
                    t.innerHTML = e,
                    ps(t),
                    hs(t.parentElement),
                    t.querySelector(kc) && new tr(t,t.querySelector(kc))
                } else
                    t.dispatchEvent(new CustomEvent("tabs:hideRelatedTab",{
                        bubbles: !0
                    }))
            }
            )).catch((function(t) {
                console.warn(t)
            }
            ))
        }
        recent() {
            const t = this.container.querySelector(Lc)
              , e = this.container.querySelector(Tc)
              , i = this.container.querySelectorAll(Sc)
              , s = t.hasAttribute(Ec) ? parseInt(t.getAttribute(Ec)) : 4
              , n = !e && i.length > 0
              , o = e && i.length >= s;
            (n || o) && (t.dispatchEvent(new CustomEvent("tabs:checkRecentTab",{
                bubbles: !0
            })),
            hs(this.container),
            t.querySelector(kc) && new tr(t,t.querySelector(kc)))
        }
    }
    Pt("related", [{
        onLoad() {
            this.section = new Ac(this)
        }
    }, Vl, st]);
    const qc = {
        ajaxDisable: "data-ajax-disable",
        shipping: "[data-shipping-estimate-form]",
        input: "[data-update-cart]",
        update: "[data-update-button]",
        bottom: "[data-cart-bottom]",
        upsellProduct: "[data-upsell-holder]",
        upsellButton: "[data-add-action-wrapper]"
    }
      , xc = {
        onLoad() {
            if (this.disabled = "true" == this.container.getAttribute(qc.ajaxDisable),
            this.disabled)
                return void (this.cart = new _c(this));
            this.cart = new ln(this);
            this.cart.init().then((()=>{
                this.cart.loadHTML()
            }
            ));
            this.container.querySelector(qc.shipping) && new qs(this)
        }
    };
    class _c {
        constructor(t) {
            this.container = t.container,
            this.inputs = this.container.querySelectorAll(qc.input),
            this.quantityWrappers = this.container.querySelectorAll(qc.qty),
            this.updateBtn = this.container.querySelector(qc.update),
            this.upsellProduct = this.container.querySelector(qc.upsellProduct),
            this.initQuantity(),
            this.initInputs(),
            this.upsellProduct && this.moveUpsell()
        }
        initQuantity() {
            zs(this.container)
        }
        moveUpsell() {
            const t = this.container.querySelector(qc.bottom);
            t.insertBefore(this.upsellProduct, t.firstChild);
            const e = this.container.querySelector(qc.upsellButton);
            new Bs(e)
        }
        initInputs() {
            this.inputs.forEach((t=>{
                t.addEventListener("change", function() {
                    this.updateBtn.classList.add("cart--dirty"),
                    this.updateBtn.classList.add("heartBeat"),
                    setTimeout(function() {
                        this.updateBtn.classList.remove("heartBeat")
                    }
                    .bind(this), 1300)
                }
                .bind(this))
            }
            ))
        }
    }
    Pt("cart", [xc, vn]),
    Pt("accordion-single", vn);
    const Pc = (t,e,i=null)=>{
        t.style.opacity = 0,
        t.style.display = e || "block",
        function e() {
            let s = parseFloat(t.style.opacity);
            (s += .1) > 1 || (t.style.opacity = s,
            requestAnimationFrame(e)),
            1 === s && "function" == typeof i && i()
        }()
    }
      , Cc = (t,e=null)=>{
        t.style.opacity = 1,
        function i() {
            (t.style.opacity -= .1) < 0 ? t.style.display = "none" : requestAnimationFrame(i),
            0 === parseFloat(t.style.opacity) && "function" == typeof e && e()
        }()
    }
      , Dc = "[data-newsletter-form]"
      , Mc = "has-success"
      , Hc = "has-error"
      , Ic = {};
    class Bc {
        constructor(t) {
            this.sessionStorage = window.sessionStorage,
            this.newsletter = t,
            this.stopSubmit = !0,
            this.isChallengePage = !1,
            this.formID = null,
            this.checkForChallengePage(),
            this.newsletterSubmit = t=>this.newsletterSubmitEvent(t),
            this.isChallengePage || this.init()
        }
        init() {
            this.newsletter.addEventListener("submit", this.newsletterSubmit),
            this.showMessage()
        }
        newsletterSubmitEvent(t) {
            this.stopSubmit && (t.preventDefault(),
            this.removeStorage(),
            this.writeStorage(),
            this.stopSubmit = !1,
            this.newsletter.submit())
        }
        checkForChallengePage() {
            this.isChallengePage = "/challenge" === window.location.pathname
        }
        writeStorage() {
            void 0 !== this.sessionStorage && this.sessionStorage.setItem("newsletter_form_id", this.newsletter.id)
        }
        readStorage() {
            this.formID = this.sessionStorage.getItem("newsletter_form_id")
        }
        removeStorage() {
            this.sessionStorage.removeItem("newsletter_form_id")
        }
        showMessage() {
            if (this.readStorage(),
            this.newsletter.id === this.formID) {
                const t = document.getElementById(this.formID);
                -1 !== window.location.search.indexOf("?customer_posted=true") ? (t.classList.remove(Hc),
                t.classList.add(Mc)) : -1 !== window.location.search.indexOf("accepts_marketing") && (t.classList.remove(Mc),
                t.classList.add(Hc)),
                this.scrollToForm(t)
            }
        }
        scrollToForm(t) {
            const e = t.getBoundingClientRect();
            e.top >= 0 && e.left >= 0 && e.bottom <= (window.innerHeight || document.documentElement.clientHeight) && e.right <= (window.innerWidth || document.documentElement.clientWidth) || setTimeout((()=>{
                window.scroll({
                    top: e.top,
                    left: 0,
                    behavior: "smooth"
                })
            }
            ), 400)
        }
        unload() {
            this.newsletter.removeEventListener("submit", this.newsletterSubmit)
        }
    }
    const $c = {
        onLoad() {
            Ic[this.id] = [];
            this.container.querySelectorAll(Dc).forEach((t=>{
                Ic[this.id].push(new Bc(t))
            }
            ))
        },
        onUnload() {
            Ic[this.id].forEach((t=>{
                "function" == typeof t.unload && t.unload()
            }
            ))
        }
    }
      , Fc = "[data-tracking-consent]"
      , Oc = "[data-confirm-cookies]"
      , Wc = "[data-close-modal]"
      , jc = "[data-popup-inner]"
      , Nc = "[data-newsletter]"
      , zc = "[data-newsletter-holder]"
      , Vc = "[data-newsletter-field]"
      , Rc = "[data-newsletter-form]"
      , Uc = "[data-promo-text]"
      , Jc = "data-popup-delay"
      , Kc = "data-cookie-name"
      , Xc = "data-target-referrer"
      , Yc = "has-value"
      , Qc = "has-success"
      , Gc = "desktop"
      , Zc = "mobile";
    let th = {};
    class eh {
        constructor(t, e) {
            this.configuration = {
                expires: null,
                path: "/",
                domain: window.location.hostname
            },
            this.name = t,
            this.value = e
        }
        write() {
            (-1 !== document.cookie.indexOf("; ") && !document.cookie.split("; ").find((t=>t.startsWith(this.name))) || -1 === document.cookie.indexOf("; ")) && (document.cookie = `${this.name}=${this.value}; expires=${this.configuration.expires}; path=${this.configuration.path}; domain=${this.configuration.domain}`)
        }
        read() {
            if (-1 !== document.cookie.indexOf("; ") && document.cookie.split("; ").find((t=>t.startsWith(this.name)))) {
                return document.cookie.split("; ").find((t=>t.startsWith(this.name))).split("=")[1]
            }
            return !1
        }
        destroy() {
            document.cookie.split("; ").find((t=>t.startsWith(this.name))) && (document.cookie = `${this.name}=null; expires=${this.configuration.expires}; path=${this.configuration.path}; domain=${this.configuration.domain}`)
        }
    }
    class ih {
        constructor(t, e) {
            this.element = e,
            this.delay = t.getAttribute(Jc),
            "always" === this.delay && this.always(),
            "delayed" === this.delay && this.delayed(),
            "bottom" === this.delay && this.bottom(),
            "idle" === this.delay && this.idle()
        }
        always() {
            Pc(this.element)
        }
        delayed() {
            setTimeout((()=>{
                Pc(this.element)
            }
            ), 1e4)
        }
        bottom() {
            window.addEventListener("scroll", (()=>{
                window.scrollY + window.innerHeight >= document.body.clientHeight && Pc(this.element)
            }
            ))
        }
        idle() {
            let t = 0;
            const e = ["mousemove", "mousedown", "click", "touchmove", "touchstart", "touchend", "keydown", "keypress"]
              , i = ["load", "resize", "scroll"]
              , s = ()=>{
                t = setTimeout((()=>{
                    t = 0,
                    Pc(this.element)
                }
                ), 6e4),
                e.forEach((t=>{
                    document.addEventListener(t, n)
                }
                )),
                i.forEach((t=>{
                    window.addEventListener(t, n)
                }
                ))
            }
              , n = ()=>{
                t && clearTimeout(t),
                e.forEach((t=>{
                    document.removeEventListener(t, n)
                }
                )),
                i.forEach((t=>{
                    window.removeEventListener(t, n)
                }
                )),
                s()
            }
            ;
            s()
        }
    }
    class sh {
        constructor(t) {
            this.el = t,
            this.locationPath = location.href,
            this.el.hasAttribute(Xc) && this.init()
        }
        init() {
            -1 !== this.locationPath.indexOf(this.el.getAttribute(Xc)) || window.Shopify.designMode || this.el.parentNode.removeChild(this.el)
        }
    }
    class nh {
        constructor(t) {
            this.popup = t,
            this.modal = document.querySelector(Fc),
            this.modalInner = this.popup.querySelector(jc),
            this.close = this.modal.querySelector(Wc),
            this.acceptButton = this.modal.querySelector(Oc),
            this.enable = "true" === this.modal.getAttribute("data-enable"),
            this.showPopup = !1,
            window.Shopify.loadFeatures([{
                name: "consent-tracking-api",
                version: "0.1"
            }], (t=>{
                if (t)
                    throw t;
                const e = window.Shopify.customerPrivacy.userCanBeTracked()
                  , i = window.Shopify.customerPrivacy.getTrackingConsent();
                this.showPopup = !e && "no_interaction" === i && this.enable,
                window.Shopify.designMode && (this.showPopup = !0),
                this.init()
            }
            ))
        }
        init() {
            this.showPopup && Pc(this.modalInner),
            this.clickEvents()
        }
        clickEvents() {
            this.close.addEventListener("click", (t=>{
                t.preventDefault(),
                window.Shopify.customerPrivacy.setTrackingConsent(!1, (()=>Cc(this.modalInner)))
            }
            )),
            this.acceptButton.addEventListener("click", (t=>{
                t.preventDefault(),
                window.Shopify.customerPrivacy.setTrackingConsent(!0, (()=>Cc(this.modalInner)))
            }
            )),
            document.addEventListener("trackingConsentAccepted", (function() {
                console.log("trackingConsentAccepted event fired")
            }
            ))
        }
        onBlockSelect(t) {
            this.popup.contains(t.target) && this.showPopup && Pc(this.modalInner)
        }
        onBlockDeselect(t) {
            this.popup.contains(t.target) && Cc(this.modalInner)
        }
    }
    class oh {
        constructor(t) {
            this.popup = t,
            this.popupInner = this.popup.querySelector(jc),
            this.close = this.popup.querySelector(Wc),
            this.cookie = new eh(this.popup.getAttribute(Kc),"user_has_closed"),
            this.isTargeted = new sh(this.popup),
            this.hasDeviceClass = "",
            this.init()
        }
        init() {
            !1 !== this.cookie.read() && !window.Shopify.designMode || (window.Shopify.designMode ? Pc(this.popupInner) : new ih(this.popup,this.popupInner),
            this.clickEvents())
        }
        clickEvents() {
            this.close.addEventListener("click", (t=>{
                t.preventDefault(),
                Cc(this.popupInner),
                this.cookie.write()
            }
            ))
        }
        onBlockSelect(t) {
            this.popup.classList.contains(Zc) && (this.hasDeviceClass = Zc),
            this.popup.classList.contains(Gc) && (this.hasDeviceClass = Gc),
            "" !== this.hasDeviceClass && this.popup.classList.remove(this.hasDeviceClass),
            this.popup.contains(t.target) && Pc(this.popupInner)
        }
        onBlockDeselect(t) {
            this.popup.contains(t.target) && Cc(this.popupInner),
            "" !== this.hasDeviceClass && this.popup.classList.add(this.hasDeviceClass)
        }
    }
    class rh {
        constructor(t) {
            this.popup = t,
            this.popupInner = this.popup.querySelector(jc),
            this.holder = this.popup.querySelector(zc),
            this.close = this.popup.querySelector(Wc),
            this.newsletterField = this.popup.querySelector(Vc),
            this.cookie = new eh(this.popup.getAttribute(Kc),"newsletter_is_closed"),
            this.form = this.popup.querySelector(Rc),
            this.isTargeted = new sh(this.popup),
            this.init()
        }
        init() {
            !1 !== this.cookie.read() && !window.Shopify.designMode || (this.show(),
            this.form.classList.contains(Qc) && this.checkForSuccess())
        }
        show() {
            window.Shopify.designMode ? Pc(this.popupInner) : new ih(this.popup,this.popupInner),
            this.inputField(),
            this.closePopup()
        }
        checkForSuccess() {
            Pc(this.popupInner),
            this.cookie.write()
        }
        closePopup() {
            this.close.addEventListener("click", (t=>{
                t.preventDefault(),
                Cc(this.popupInner),
                this.cookie.write()
            }
            ))
        }
        inputField() {
            this.newsletterField.addEventListener("input", (()=>{
                "" !== this.newsletterField.value && this.holder.classList.add(Yc, "" !== this.newsletterField.value)
            }
            )),
            this.newsletterField.addEventListener("focus", (()=>{
                "" !== this.newsletterField.value && this.holder.classList.add(Yc, "" !== this.newsletterField.value)
            }
            )),
            this.newsletterField.addEventListener("focusout", (()=>{
                setTimeout((()=>{
                    this.holder.classList.remove(Yc)
                }
                ), 2e3)
            }
            ))
        }
        onBlockSelect(t) {
            this.popup.contains(t.target) && Pc(this.popupInner)
        }
        onBlockDeselect(t) {
            this.popup.contains(t.target) && Cc(this.popupInner)
        }
    }
    Pt("popups", [{
        onLoad() {
            th[this.id] = [];
            this.container.querySelectorAll(Fc).forEach((t=>{
                th[this.id].push(new nh(t))
            }
            ));
            this.container.querySelectorAll(Nc).forEach((t=>{
                th[this.id].push(new rh(t))
            }
            ));
            this.container.querySelectorAll(Uc).forEach((t=>{
                th[this.id].push(new oh(t))
            }
            ))
        },
        onBlockSelect(t) {
            th[this.id].forEach((e=>{
                "function" == typeof e.onBlockSelect && e.onBlockSelect(t)
            }
            ))
        },
        onBlockDeselect(t) {
            th[this.id].forEach((e=>{
                "function" == typeof e.onBlockDeselect && e.onBlockDeselect(t)
            }
            ))
        }
    }, $c]);
    const ah = (t,e="",i)=>((i = i || document.createElement("div")).classList.add(e),
    t.parentNode.insertBefore(i, t),
    i.appendChild(t));
    document.addEventListener("DOMContentLoaded", (function() {
        Ct("*"),
        window.theme.settings.animate_scroll && (u.init({
            once: !0
        }),
        document.body.classList.add("aos-initialized"),
        document.body.classList.add("theme-animate-scroll")),
        window.theme.settings.animate_hover && document.body.classList.add("theme-animate-hover"),
        document.addEventListener("lazyloaded", (function(t) {
            const e = t.target.parentNode;
            e.classList.contains("lazy-image") && (e.style.backgroundImage = "none")
        }
        ));
        document.querySelectorAll(".rte table").forEach((t=>{
            ah(t, "rte__table-wrapper")
        }
        ));
        document.querySelectorAll('.rte iframe[src*="youtube.com/embed"], .rte iframe[src*="player.vimeo"], .rte iframe#admin_bar_iframe').forEach((t=>{
            ah(t, "rte__video-wrapper")
        }
        )),
        document.addEventListener("mousedown", (()=>{
            document.body.classList.remove("focus-enabled")
        }
        )),
        document.addEventListener("keyup", (t=>{
            9 === t.keyCode && document.body.classList.add("focus-enabled")
        }
        )),
        window.navigator.cookieEnabled && (document.documentElement.className = document.documentElement.className.replace("supports-no-cookies", "supports-cookies")),
        function(t) {
            t = t || {};
            var e = window.location.hash
              , i = document.getElementById(e.slice(1));
            if (i && t.ignore && i.matches(t.ignore))
                return !1;
            e && i && $t(i, t)
        }(),
        Ft(),
        "scrollBehavior"in document.documentElement.style || Ki({
            url: window.theme.assets.smoothscroll
        })
    }
    ))
}(themeVendor.BodyScrollLock, themeVendor.MicroModal, themeVendor.Rellax, themeVendor.Flickity, themeVendor.themeCurrency, themeVendor.Sqrl, themeVendor.themeAddresses, themeVendor.axios, themeVendor.FlickityFade, themeVendor.Poppy, themeVendor.ellipsis, themeVendor.FlickitySync, themeVendor.AOS);
//# sourceMappingURL=theme.js.map