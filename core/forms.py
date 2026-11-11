from decimal import Decimal
from django import forms
from .models import Product, Client, ProductVariant, Location, ProductImage, Barcode

BRAND_CHOICES = [
    ('Gucci', 'Gucci'), ('Prada', 'Prada'), ('Louis Vuitton', 'Louis Vuitton'), 
    ('Hermès', 'Hermès'), ('Chanel', 'Chanel'), ('Dior', 'Dior'), 
    ('Balenciaga', 'Balenciaga'), ('Saint Laurent', 'Saint Laurent'), 
    ('Burberry', 'Burberry'), ('Fendi', 'Fendi'), ('Versace', 'Versace'),
    ('Valentino', 'Valentino'), ('Givenchy', 'Givenchy'), ('Bottega Veneta', 'Bottega Veneta'),
    ('Loewe', 'Loewe'), ('Celine', 'Celine'), ('Alexander McQueen', 'Alexander McQueen'),
    ('Dolce & Gabbana', 'Dolce & Gabbana'), ('Tom Ford', 'Tom Ford'), ('The Row', 'The Row'),
    ('Brunello Cucinelli', 'Brunello Cucinelli'), ('Loro Piana', 'Loro Piana'),
    ('Other', 'Other')
]

BRAND_SUGGESTIONS = [
    "A", "A.P.C.", "Aadnevik", "Acne Studios", "Agnès b.", "Aimé Leon Dore", "Akris", "Alaïa",
    "Alessandra Rich", "Alexander McQueen", "Alexandre Vauthier", "Alexis Mabille", "Alice + Olivia",
    "Altuzarra", "Amanda Wakeley", "Amiri", "Ami Paris", "Ann Demeulemeester", "Aquazzura",
    "Balenciaga", "Balmain", "Bao Bao Issey Miyake", "BAPE (A Bathing Ape)", "Barbara Bui", "Berluti",
    "Blumarine", "Bode", "Boglioli", "Bottega Veneta", "Brioni", "Brunello Cucinelli", "Burberry",
    "By Far", "Boss (Hugo Boss)", "Bally", "Belstaff", "ba&sh",
    "C.P. Company", "Celine", "Cerruti 1881", "Chalayan", "Charles Jeffrey Loverboy", "Charvet",
    "Chloé", "Chrome Hearts", "Christian Dior", "Christian Lacroix", "Christian Louboutin",
    "Christopher Kane", "Church’s", "Comme des Garçons", "Courrèges", "Craig Green", "Coach",
    "Corneliani",
    "Damir Doma", "Delvaux", "Derek Lam", "Diane von Furstenberg", "Diesel Black Gold",
    "Dolce & Gabbana", "Dries Van Noten", "Dsquared2", "Dunhill", "Delpozo", "Dorothee Schumacher",
    "Deveaux", "Dion Lee", "Dodo Bar Or", "DKNY",
    "E. Tautz", "Eera", "Eileen Fisher", "Elie Saab", "Elisabetta Franchi", "Emilio Pucci",
    "Emporio Armani", "Ernest Leoty", "Etro", "Equipment", "Ermanno Scervino", "Eskandar",
    "Ermenegildo Zegna Couture",
    "Fendi", "Fear of God", "Fenty", "Ferragamo (Salvatore Ferragamo)", "Fiorucci", "Frame",
    "Frankie Shop", "Fred Perry", "Furla", "Facetasm", "Faith Connexion", "Fusalp", "Forte Forte",
    "Filippa K", "Freda Salvador",
    "Ganni", "Gareth Pugh", "GCDS", "Giorgio Armani", "Giambattista Valli", "Gianfranco Ferré",
    "Givenchy", "Golden Goose", "Goyard", "Gucci", "Guidi", "Gabriela Hearst", "Giuliva Heritage",
    "Hackett London", "Haider Ackermann", "Halston", "Helmut Lang", "Hermès", "Heron Preston",
    "Hogan", "Homme Plissé Issey Miyake", "House of Holland", "Hugo Boss", "Hood By Air",
    "Iceberg", "Incotex", "Isabel Marant", "Issey Miyake", "IRO", "Iris van Herpen", "Isaia",
    "Ivana Helsinki", "Il Bisonte", "Inès de la Fressange Paris", "Intimissimi",
    "J Brand", "JW Anderson", "Jacquemus", "Jil Sander", "Jimmy Choo", "John Elliott", "John Galliano",
    "John Lobb", "John Varvatos", "Joseph", "Just Cavalli",
    "K-Way", "Khaite", "Kenzo", "Kiton", "Koché", "Kris Van Assche", "Ksubi", "Kurt Geiger",
    "L.B.M. 1911", "L.K. Bennett", "Lacoste", "Lanvin", "Laurence Dacade", "Lemaire",
    "Les Copains", "Loewe", "Longchamp", "Loro Piana", "Louis Vuitton", "Lucchese",
    "Ludovic de Saint Sernin", "Lululemon",
    "Maje", "Maison Kitsuné", "Maison Margiela", "Manolo Blahnik", "Marc Jacobs", "Marine Serre",
    "Marni", "Mary Katrantzou", "Massimo Alba", "Max Mara", "Michael Kors Collection", "Missoni",
    "Miu Miu", "Moncler", "Montblanc", "Moschino", "Mugler",
    "N.Hoolywood", "Nanushka", "Narciso Rodriguez", "Neil Barrett", "Neighborhood", "New & Lingwood",
    "N°21 (Numero Ventuno)", "Norma Kamali",
    "Off-White", "Oscar de la Renta", "Officine Générale", "Oliver Spencer", "Onitsuka Tiger",
    "Opening Ceremony", "Orlebar Brown", "Osklen",
    "Paco Rabanne", "Palm Angels", "Pal Zileri", "Parajumpers", "Paul Smith", "Paul & Shark",
    "Philipp Plein", "Pierre Balmain", "Pinko", "Polo Ralph Lauren", "Prada", "Proenza Schouler",
    "Patou", "Pyer Moss", "Piazza Sempione",
    "Qasimi", "Qi Cashmere", "Qeelin", "Quoddy",
    "Rag & Bone", "Ralph Lauren", "Rami Al Ali", "Re/Done", "Reformation", "Reiss", "Rick Owens",
    "Roberto Cavalli", "Rochas", "Rodarte", "Roland Mouret", "Roksanda", "Roy Roger's",
    "Russell & Bromley",
    "Sacai", "Saint Laurent", "Salvatore Ferragamo", "Sandro", "S.T. Dupont", "S Max Mara",
    "See by Chloé", "Sergio Rossi", "Simone Rocha", "Sies Marjan", "Sonia Rykiel", "Sportmax",
    "Stella McCartney", "Stone Island", "Strellson", "Stuart Weitzman", "Stüssy", "Supreme",
    "Sunspel", "Smythson", "Schiaparelli", "Sankuanz",
    "Tagliatore", "Takahiromiyashita The Soloist", "Ted Baker", "Thom Browne", "Theory",
    "The Kooples", "The Row", "Thom Sweeney", "Tiger of Sweden", "Tod’s", "Tom Ford", "Tumi",
    "Ulla Johnson", "Undercover", "Unravel Project", "Ultracor",
    "Valentino", "Valextra", "Van Cleef & Arpels", "Versace", "Vetements", "Via Spiga",
    "Victoria Beckham", "Viktor & Rolf", "Vivetta", "Vivienne Westwood", "Wacko Maria",
    "Wales Bonner", "Walter Van Beirendonck", "Wolford", "Woolrich", "Wooyoungmi", "Wtaps",
    "Wanda Nylon", "WANT Les Essentiels", "Whistles",
    "Xander Zhou", "Xacus", "Xirena", "Xenia Design",
    "Y-3", "Y/Project", "Yohji Yamamoto", "Young Versace", "Yves Salomon", "YMC (You Must Create)",
    "Yigal Azrouël", "Yvonne Léon",
    "Zadig & Voltaire", "Zanellato", "Zegna (Ermenegildo Zegna)", "Zimmermann", "Zimmerli", "Z Zegna",
]

COLOR_SUGGESTIONS = [
    "Black",
    "White", 
    "Beige",
    "Brown",
    "Navy",
    "Grey",
    "Red",
    "Pink",
    "Green",
    "Blue",
]

MATERIAL_CHOICES = [
    ('Cotton', 'Cotton'), ('Silk', 'Silk'), ('Wool', 'Wool'), ('Cashmere', 'Cashmere'),
    ('Linen', 'Linen'), ('Leather', 'Leather'), ('Denim', 'Denim'), ('Velvet', 'Velvet'),
    ('Satin', 'Satin'), ('Chiffon', 'Chiffon'), ('Tweed', 'Tweed'), ('Polyester', 'Polyester'),
    ('Viscose', 'Viscose'), ('Nylon', 'Nylon'), ('Elastane', 'Elastane'),
    ('Other', 'Other'), ('Blend', 'Blend')
]

class LuxuryProductForm(forms.ModelForm):
    """Comprehensive luxury product registration form"""
    
    class Meta:
        model = Product
        fields = [
            'brand', 'name', 'category', 'collection', 'season', 'description',
            'base_sku', 'supplier_product_code',
            'material', 'material_composition',
            'condition', 'release_year', 'is_limited_edition',
            'has_box', 'has_dust_bag', 'has_warranty_card', 'has_care_card', 'has_extras',
            'packaging_condition', 'packaging_notes', 'provenance_notes',
            'country_of_origin',
            'image',
            'internal_tags', 'keywords', 'display_notes',
        ]
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control', 'list': 'brand-options', 'placeholder': 'Search or type a brand'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'collection': forms.TextInput(attrs={'class': 'form-control'}),
            'season': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. SS25, FW24'}),
            'description': forms.Textarea(attrs={'class': 'form-control rich-text', 'rows': 4, 'placeholder': 'Optional details, styling notes, provenance'}),
            'base_sku': forms.TextInput(attrs={'class': 'form-control font-monospace'}),
            'supplier_product_code': forms.TextInput(attrs={'class': 'form-control'}),
            'material': forms.Select(choices=MATERIAL_CHOICES, attrs={'class': 'form-select', 'data-allow-custom': 'true'}),
            'material_composition': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. 80% Wool, 20% Silk'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'release_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': 2100}),
            'is_limited_edition': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_box': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_dust_bag': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_warranty_card': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_care_card': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_extras': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'packaging_condition': forms.Select(attrs={'class': 'form-select'}),
            'packaging_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'provenance_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Authenticity, purchase provenance, receipts'}),
            'country_of_origin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'France, Italy, Switzerland'}),
            'internal_tags': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'VIP-favorite, holiday, gala (comma-separated)'}),
            'keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'display_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.fields['image'].required = True
        self.fields['base_sku'].required = False

        # No silent defaults on a new piece: staff pick category and material
        if not self.instance.pk:
            self.initial.setdefault('category', '')
            self.fields['category'].choices = [('', 'Select a category')] + list(Product.CATEGORY_CHOICES)
            self.fields['category'].widget.choices = self.fields['category'].choices
        material = self.fields['material']
        material.widget.choices = [('', 'Select a material')] + [c for c in material.widget.choices if c[0]]
        if 'packaging_condition' in self.fields:
            pc = self.fields['packaging_condition']
            pc.choices = [('', 'Select condition')] + [c for c in pc.choices if c[0]]
        self.fields['base_sku'].widget.attrs.setdefault('placeholder', 'Auto-generated if left blank')
        self.fields['image'].widget.attrs.update({'class': 'form-control', 'accept': 'image/*'})

    def clean_base_sku(self):
        base_sku = self.cleaned_data.get('base_sku')
        if base_sku:
            return base_sku
        
        brand = (self.cleaned_data.get('brand') or 'UNK').upper()[:3]
        category = (self.cleaned_data.get('category') or 'GEN').upper()[:3]
        
        import random
        while True:
            rand_suffix = str(random.randint(1000, 9999))
            candidate = f"{brand}-{category}-{rand_suffix}"
            if not Product.objects.filter(base_sku=candidate).exists():
                return candidate
        
        if self.user and self.user.is_associate():
            manager_only_fields = [
                'supplier_product_code',
                'has_box', 'has_dust_bag', 'has_warranty_card', 'has_care_card', 'has_extras',
                'packaging_condition', 'packaging_notes', 'provenance_notes',
                'country_of_origin',
            ]
            for field in manager_only_fields:
                if field in self.fields:
                    self.fields[field].widget = forms.HiddenInput()
                    self.fields[field].required = False

class ProductVariantForm(forms.ModelForm):
    """Form for product variants with luxury-specific fields"""
    barcode = forms.CharField(required=False, label='Barcode / EAN / UPC', widget=forms.HiddenInput())
    barcode_type = forms.ChoiceField(
        required=False,
        choices=Barcode.Type.choices,
        initial=Barcode.Type.EAN13,
        label='Barcode type',
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = ProductVariant
        fields = [
            'sku', 'color', 'size',
            'cost_price', 'retail_price',
            'barcode', 'barcode_type',
            'initial_quantity', 'minimum_stock_level',
        ]
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control font-monospace'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'list': 'color-suggestions'}),
            'size': forms.TextInput(attrs={'class': 'form-control'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'retail_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'barcode': forms.HiddenInput(),
            'barcode_type': forms.HiddenInput(),
            'initial_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'minimum_stock_level': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['sku'].required = False
        
        self.fields['cost_price'].required = True
        self.fields['cost_price'].initial = Decimal('0.00')
        
        if user and not user.is_owner():
            # Disabled, not just hidden: Django ignores posted values for disabled fields
            self.fields['cost_price'].widget = forms.HiddenInput()
            self.fields['cost_price'].required = False
            self.fields['cost_price'].disabled = True
            self.fields['cost_price'].initial = Decimal('0.00')
            
        self.fields['minimum_stock_level'].initial = 1
        self.fields['barcode_type'].initial = Barcode.Type.EAN13
        self.fields['minimum_stock_level'].required = False
        self.fields['barcode_type'].required = False
        self.fields['barcode'].required = False
        
        self.fields['initial_quantity'].required = True
        self.fields['initial_quantity'].widget.attrs['min'] = 1
        self.fields['initial_quantity'].initial = 1
        self.fields['retail_price'].required = True
        self.fields['retail_price'].widget.attrs.setdefault('min', '0')
        self.fields['sku'].widget.attrs.setdefault('placeholder', 'Unique SKU per variant')
        self.fields['color'].widget.attrs.setdefault('placeholder', 'e.g. Noir, Rouge H')
        self.fields['size'].widget.attrs.setdefault('placeholder', 'EU 38, 25 cm')

    def clean_cost_price(self):
        cost_price = self.cleaned_data.get('cost_price')
        if cost_price is None:
            return Decimal('0.00')
        return cost_price
    
    def clean_barcode(self):
        code = self.cleaned_data.get('barcode')
        if not code:
            return code
        existing = Barcode.objects.filter(code=code)
        if self.instance.pk:
            existing = existing.exclude(variant=self.instance)
        if existing.exists():
            raise forms.ValidationError("This barcode is already linked to another variant.")
        return code

ProductVariantFormSet = forms.inlineformset_factory(
    Product, ProductVariant,
    form=ProductVariantForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
    error_messages={
        'too_few_forms': 'Please fill out all the required fields for at least one variant.',
    }
)

class ProductImageForm(forms.ModelForm):
    """Form for additional product images"""
    
    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary', 'order']
        widgets = {
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

ProductImageFormSet = forms.inlineformset_factory(
    Product, ProductImage,
    form=ProductImageForm,
    extra=3,
    can_delete=True,
)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['brand', 'name', 'category', 'base_sku', 'collection', 'season', 'description', 'material', 'material_composition', 'image', 'is_limited_edition']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control', 'list': 'brand-options', 'placeholder': 'Brand'}),
            'category': forms.Select(choices=Product.CATEGORY_CHOICES, attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'base_sku': forms.TextInput(attrs={'class': 'form-control font-monospace', 'placeholder': 'Base SKU'}),
            'collection': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'season': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'material': forms.Select(choices=MATERIAL_CHOICES, attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'material_composition': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'e.g. 80% Wool, 20% Silk or specific material name'}),
            'is_limited_edition': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['base_sku'].required = False
        self.fields['base_sku'].widget.attrs['placeholder'] = 'Auto-generated if left blank'

    def clean_base_sku(self):
        base_sku = self.cleaned_data.get('base_sku')
        if base_sku:
            return base_sku
        
        brand = (self.cleaned_data.get('brand') or 'UNK').upper()[:3]
        category = (self.cleaned_data.get('category') or 'GEN').upper()[:3]
        
        import random
        while True:
            rand_suffix = str(random.randint(1000, 9999))
            candidate = f"{brand}-{category}-{rand_suffix}"
            if not Product.objects.filter(base_sku=candidate).exists():
                return candidate

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'phone', 'email', 'birthday', 'notes', 'prefers_communication', 'loyalty_tier']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'prefers_communication': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


from .models import Promotion, Product as ProductModel

class PromotionForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        queryset=ProductModel.objects.filter(is_archived=False),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select products for this promotion (only for 'Selected Products' type)"
    )

    class Meta:
        model = Promotion
        fields = [
            'name', 'code', 'description', 'promo_type',
            'discount_value', 'buy_quantity', 'get_quantity',
            'silver_discount', 'gold_discount', 'platinum_discount',
            'applies_to', 'category', 'brand', 'customer_tier',
            'min_purchase', 'min_items',
            'start_date', 'end_date', 'is_active',
            'max_uses', 'max_uses_per_customer'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['products'].initial = self.instance.product_links.values_list('product_id', flat=True)
