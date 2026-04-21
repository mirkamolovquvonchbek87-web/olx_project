(function ($) {
    $(document).ready(function () {
        const categorySelect = $('#id_category');
        const attributeField = $('#id_attribute');

        if (!categorySelect.length || !attributeField.length) return;

        // Hide original fields
        categorySelect.closest('.form-row').hide();
        attributeField.closest('.form-row').hide();

        const container = $('<div class="dynamic-category-container" style="margin-bottom: 20px; padding: 15px; background: #fff; border: 1px solid #ddd;"><h3>Kategoriya tanlang</h3></div>');
        categorySelect.closest('fieldset').prepend(container);

        const attrContainer = $('<div class="dynamic-attributes-container" style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border: 1px solid #ddd; display: none;"></div>');
        categorySelect.closest('fieldset').append(attrContainer);

        let currentCategory = categorySelect.val() || null;
        let schemaCache = [];

        function loadRoots() {
            $.getJSON('/api/categories/roots/', function (data) {
                renderSelect(data, 0, 'Asosiy kategoriya');
            });
        }

        function loadChildren(parentId, level) {
            $.getJSON(`/api/categories/${parentId}/children/`, function (data) {
                if (data.length > 0) {
                    renderSelect(data, level, 'Kichik kategoriya');
                } else {
                    currentCategory = parentId;
                    categorySelect.val(parentId);
                    loadAttributes(parentId);
                }
            });
        }

        function renderSelect(data, level, placeholder) {
            $('.dynamic-cat-select').filter(function () {
                return $(this).data('level') >= level;
            }).remove();

            attrContainer.hide().empty().append('<h3>Qo\'shimcha xususiyatlar</h3>');
            attributeField.val(''); // Clear old attributes

            const select = $('<select class="dynamic-cat-select" style="display: block; width: 100%; max-width: 400px; margin-bottom: 10px; padding: 8px; border: 1px solid #ccc; border-radius: 4px;"></select>');
            select.data('level', level);
            select.append(`<option value="">-- ${placeholder} --</option>`);

            data.forEach(item => {
                select.append(`<option value="${item.id}">${item.name}</option>`);
            });

            select.on('change', function () {
                const val = $(this).val();
                // Clear lowers
                $('.dynamic-cat-select').filter(function () {
                    return $(this).data('level') > level;
                }).remove();

                attrContainer.hide().empty().append('<h3>Qo\'shimcha xususiyatlar</h3>');
                attributeField.val('');
                currentCategory = null;
                categorySelect.val('');

                if (val) {
                    loadChildren(val, level + 1);
                }
            });

            container.append(select);
        }

        function loadAttributes(categoryId) {
            $.getJSON(`/api/categories/${categoryId}/attributes/`, function (data) {
                schemaCache = data;
                if (data && data.length > 0) {
                    renderAttributes(data);
                }
            });
        }

        function renderAttributes(schema) {
            attrContainer.show();
            // Parse existing attributes if any
            let existing = {};
            try {
                if (attributeField.val()) {
                    existing = JSON.parse(attributeField.val());
                }
            } catch (e) { }

            schema.forEach(field => {
                const wrapper = $('<div style="margin-bottom: 15px;"></div>');
                wrapper.append(`<label style="display:block; font-weight:bold; margin-bottom: 5px;">${field.label} ${field.required ? '<span style="color:red;">*</span>' : ''}</label>`);

                let input;
                const fieldName = field.name;
                const value = existing[fieldName] || '';

                if (field.type === 'select') {
                    input = $(`<select data-name="${fieldName}" class="dynamic-attr-field" style="width: 100%; max-width: 400px; padding: 8px; border: 1px solid #ccc; border-radius: 4px;">`);
                    input.append(`<option value="">Tanlang</option>`);
                    (field.options || []).forEach(opt => {
                        input.append(`<option value="${opt}" ${value === opt ? 'selected' : ''}>${opt}</option>`);
                    });
                } else if (field.type === 'multiselect') {
                    input = $(`<select data-name="${fieldName}" multiple class="dynamic-attr-field" style="width: 100%; max-width: 400px; padding: 8px; height: 120px; border: 1px solid #ccc; border-radius: 4px;">`);
                    const valArray = Array.isArray(value) ? value : [];
                    (field.options || []).forEach(opt => {
                        input.append(`<option value="${opt}" ${valArray.includes(opt) ? 'selected' : ''}>${opt}</option>`);
                    });
                } else if (field.type === 'int') {
                    input = $(`<input type="number" data-name="${fieldName}" class="dynamic-attr-field" value="${value}" placeholder="${field.placeholder || ''}" style="width: 100%; max-width: 400px; padding: 8px; border: 1px solid #ccc; border-radius: 4px;">`);
                } else {
                    input = $(`<input type="text" data-name="${fieldName}" class="dynamic-attr-field" value="${value}" placeholder="${field.placeholder || ''}" style="width: 100%; max-width: 400px; padding: 8px; border: 1px solid #ccc; border-radius: 4px;">`);
                }

                if (field.required) {
                    input.attr('required', 'required');
                }

                input.on('change', updateAttributesJson);
                wrapper.append(input);
                attrContainer.append(wrapper);
            });
        }

        function updateAttributesJson() {
            const result = {};
            $('.dynamic-attr-field').each(function () {
                const name = $(this).data('name');
                const val = $(this).val();
                if (val !== null && val !== '') {
                    result[name] = val;
                }
            });
            attributeField.val(JSON.stringify(result));
        }

        // Init
        if (!currentCategory) {
            loadRoots();
        } else {
            // For editing, simplistic approach: just reload roots and user must reselect.
            // A more complex approach would fetch parent chain and populate all selects.
            // Let's at least show the current attribute box if attributes exist.
            loadRoots();
            if (attributeField.val()) {
                loadAttributes(currentCategory);
            }
        }

        // Handle auto updates on focusout and form submit
        $('form').on('submit', function () {
            updateAttributesJson();
        });

    });
})(django.jQuery);
