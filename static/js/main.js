(function () {
    'use strict';

    // Mobile nav toggle
    var navToggle = document.getElementById('navToggle');
    var navLinks = document.getElementById('navLinks');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            navLinks.classList.toggle('open');
        });
    }

    // Auto-submit filters when selects change
    var filterForm = document.getElementById('courseFilters');
    if (filterForm) {
        filterForm.querySelectorAll('select').forEach(function (sel) {
            sel.addEventListener('change', function () { filterForm.submit(); });
        });
    }

    // Tabs on course detail
    var tabs = document.querySelectorAll('.tab');
    if (tabs.length) {
        tabs.forEach(function (tab) {
            tab.addEventListener('click', function () {
                document.querySelectorAll('.tab').forEach(function (t) { t.classList.remove('active'); });
                document.querySelectorAll('.tab-panel').forEach(function (p) { p.classList.remove('active'); });
                tab.classList.add('active');
                var panel = document.getElementById('tab-' + tab.dataset.tab);
                if (panel) { panel.classList.add('active'); }
            });
        });
    }

    // Auto-dismiss toasts
    document.querySelectorAll('.toast').forEach(function (toast) {
        setTimeout(function () {
            toast.style.transition = 'opacity .4s ease, transform .4s ease';
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(20px)';
            setTimeout(function () { toast.remove(); }, 450);
        }, 4000);
    });
})();
