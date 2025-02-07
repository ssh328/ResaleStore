import {
	ClassicEditor,
	AccessibilityHelp,
	Alignment,
	AutoImage,
	Autosave,
	SimpleUploadAdapter,
//	Base64UploadAdapter,
	Bold,
	Essentials,
	GeneralHtmlSupport,
	ImageBlock,
	ImageCaption,
	ImageInline,
	ImageInsert,
	ImageInsertViaUrl,
	ImageResize,
	ImageStyle,
	ImageToolbar,
	ImageUpload,
	Italic,
	Link,
	List,
	Paragraph,
	SelectAll,
	Strikethrough,
	Underline,
	Undo
} from 'ckeditor5';

const editorConfig = {
	toolbar: {
		items: [
			'undo',
			'redo',
			'|',
			'selectAll',
			'|',
			'bold',
			'italic',
			'underline',
			'strikethrough',
			'|',
			'link',
			'insertImage',
			'|',
			'alignment',
			'|',
			'bulletedList',
			'numberedList',
			'|',
			'accessibilityHelp'
		],
		shouldNotGroupWhenFull: false
	},
	plugins: [
		AccessibilityHelp,
		Alignment,
		AutoImage,
		Autosave,
		SimpleUploadAdapter,
//		Base64UploadAdapter,
		Bold,
		Essentials,
		GeneralHtmlSupport,
		ImageBlock,
		ImageCaption,
		ImageInline,
		ImageInsert,
		ImageInsertViaUrl,
		ImageResize,
		ImageStyle,
		ImageToolbar,
		ImageUpload,
		Italic,
		Link,
		List,
		Paragraph,
		SelectAll,
		Strikethrough,
		Underline,
		Undo
	],
	htmlSupport: {
		allow: [
			{
				name: /^.*$/,
				styles: true,
				attributes: true,
				classes: true
			}
		]
	},
	image: {
		toolbar: [
			'toggleImageCaption',
			'imageTextAlternative',
			'|',
			'imageStyle:inline',
			'imageStyle:wrapText',
			'imageStyle:breakText',
			'|',
			'resizeImage'
		]
	},
	link: {
		addTargetToExternalLinks: true,
		defaultProtocol: 'https://',
		decorators: {
			toggleDownloadable: {
				mode: 'manual',
				label: 'Downloadable',
				attributes: {
					download: 'file'
				}
			}
		}
	},
	placeholder: '사진을 1장 이상 등록해 주세요!',
	simpleUpload: {
	    uploadUrl: 'http://127.0.0.1:5000/posts/new-products-post',
	    withCredentials: true,
	    headers: {
                'X-CSRF-TOKEN': 'CSRF-Token'
        }
	}
};

ClassicEditor.create(document.querySelector('#editor'), editorConfig)

//const {
//	ClassicEditor,
//	AutoImage,
//	Autosave,
//	BlockQuote,
//	Bold,
//	CloudServices,
//	Essentials,
//	Heading,
//	ImageBlock,
//	ImageCaption,
//	ImageInline,
//	ImageInsert,
//	ImageInsertViaUrl,
//	ImageResize,
//	ImageStyle,
//	ImageTextAlternative,
//	ImageToolbar,
//	ImageUpload,
//	Indent,
//	IndentBlock,
//	Italic,
//	Link,
//	LinkImage,
//	Paragraph,
//	SimpleUploadAdapter,
//	SpecialCharacters,
//	Table,
//	TableCaption,
//	TableCellProperties,
//	TableColumnResize,
//	TableProperties,
//	TableToolbar,
//	Underline
//} = window.CKEDITOR;
//
///**
// * This is a 24-hour evaluation key. Create a free account to use CDN: https://portal.ckeditor.com/checkout?plan=free
// */
////const LICENSE_KEY =
////	'eyJhbGciOiJFUzI1NiJ9.eyJleHAiOjE3MzYwMzUxOTksImp0aSI6IjdhYTA3ZmUwLTM4NzQtNGE2My05YzFiLWQ4ZWQ0YTZkNDM3YyIsInVzYWdlRW5kcG9pbnQiOiJodHRwczovL3Byb3h5LWV2ZW50LmNrZWRpdG9yLmNvbSIsImRpc3RyaWJ1dGlvbkNoYW5uZWwiOlsiY2xvdWQiLCJkcnVwYWwiLCJzaCJdLCJ3aGl0ZUxhYmVsIjp0cnVlLCJsaWNlbnNlVHlwZSI6InRyaWFsIiwiZmVhdHVyZXMiOlsiKiJdLCJ2YyI6IjBlOTIyYWJhIn0.DXeaAofEs7YBz_iARES10HB9OhRtjNvUcb7BtTyOXD-oawJ0922tX2jxLImABOWKY3vgdZO3yOIlxyO8WtFWbQ';
//
//const editorConfig = {
//	toolbar: {
//		items: [
//			'heading',
//			'|',
//			'bold',
//			'italic',
//			'underline',
//			'|',
//			'specialCharacters',
//			'link',
//			'insertImage',
//			'insertTable',
//			'blockQuote',
//			'|',
//			'outdent',
//			'indent'
//		],
//		shouldNotGroupWhenFull: false
//	},
//	plugins: [
//		AutoImage,
//		Autosave,
//		BlockQuote,
//		Bold,
//		CloudServices,
//		Essentials,
//		Heading,
//		ImageBlock,
//		ImageCaption,
//		ImageInline,
//		ImageInsert,
//		ImageInsertViaUrl,
//		ImageResize,
//		ImageStyle,
//		ImageTextAlternative,
//		ImageToolbar,
//		ImageUpload,
//		Indent,
//		IndentBlock,
//		Italic,
//		Link,
//		LinkImage,
//		Paragraph,
//		SimpleUploadAdapter,
//		SpecialCharacters,
//		Table,
//		TableCaption,
//		TableCellProperties,
//		TableColumnResize,
//		TableProperties,
//		TableToolbar,
//		Underline
//	],
//	heading: {
//		options: [
//			{
//				model: 'paragraph',
//				title: 'Paragraph',
//				class: 'ck-heading_paragraph'
//			},
//			{
//				model: 'heading1',
//				view: 'h1',
//				title: 'Heading 1',
//				class: 'ck-heading_heading1'
//			},
//			{
//				model: 'heading2',
//				view: 'h2',
//				title: 'Heading 2',
//				class: 'ck-heading_heading2'
//			},
//			{
//				model: 'heading3',
//				view: 'h3',
//				title: 'Heading 3',
//				class: 'ck-heading_heading3'
//			},
//			{
//				model: 'heading4',
//				view: 'h4',
//				title: 'Heading 4',
//				class: 'ck-heading_heading4'
//			},
//			{
//				model: 'heading5',
//				view: 'h5',
//				title: 'Heading 5',
//				class: 'ck-heading_heading5'
//			},
//			{
//				model: 'heading6',
//				view: 'h6',
//				title: 'Heading 6',
//				class: 'ck-heading_heading6'
//			}
//		]
//	},
//	image: {
//		toolbar: [
//			'toggleImageCaption',
//			'imageTextAlternative',
//			'|',
//			'imageStyle:inline',
//			'imageStyle:wrapText',
//			'imageStyle:breakText',
//			'|',
//			'resizeImage'
//		]
//	},
//	initialData:
//		'<h2>Evaluation license key 🔑</h2>\n<p>\n\tAn evaluation key is being used in this editor. <a href="https://portal.ckeditor.com/checkout?plan=free">\n\t\tCreate an account to use your own license keys.\n\t</a>\n</p>\n\n<h2>Congratulations on setting up CKEditor 5! 🎉</h2>\n<p>\n\tYou\'ve successfully created a CKEditor 5 project. This powerful text editor\n\twill enhance your application, enabling rich text editing capabilities that\n\tare customizable and easy to use.\n</p>\n<h3>What\'s next?</h3>\n<ol>\n\t<li>\n\t\t<strong>Integrate into your app</strong>: time to bring the editing into\n\t\tyour application. Take the code you created and add to your application.\n\t</li>\n\t<li>\n\t\t<strong>Explore features:</strong> Experiment with different plugins and\n\t\ttoolbar options to discover what works best for your needs.\n\t</li>\n\t<li>\n\t\t<strong>Customize your editor:</strong> Tailor the editor\'s\n\t\tconfiguration to match your application\'s style and requirements. Or\n\t\teven write your plugin!\n\t</li>\n</ol>\n<p>\n\tKeep experimenting, and don\'t hesitate to push the boundaries of what you\n\tcan achieve with CKEditor 5. Your feedback is invaluable to us as we strive\n\tto improve and evolve. Happy editing!\n</p>\n<h3>Helpful resources</h3>\n<ul>\n\t<li>📝 <a href="https://portal.ckeditor.com/checkout?plan=free">Trial sign up</a>,</li>\n\t<li>📕 <a href="https://ckeditor.com/docs/ckeditor5/latest/installation/index.html">Documentation</a>,</li>\n\t<li>⭐️ <a href="https://github.com/ckeditor/ckeditor5">GitHub</a> (star us if you can!),</li>\n\t<li>🏠 <a href="https://ckeditor.com">CKEditor Homepage</a>,</li>\n\t<li>🧑‍💻 <a href="https://ckeditor.com/ckeditor-5/demo/">CKEditor 5 Demos</a>,</li>\n</ul>\n<h3>Need help?</h3>\n<p>\n\tSee this text, but the editor is not starting up? Check the browser\'s\n\tconsole for clues and guidance. It may be related to an incorrect license\n\tkey if you use premium features or another feature-related requirement. If\n\tyou cannot make it work, file a GitHub issue, and we will help as soon as\n\tpossible!\n</p>\n',
//	language: 'ko',
////	licenseKey: LICENSE_KEY,
//	link: {
//		addTargetToExternalLinks: true,
//		defaultProtocol: 'https://',
//		decorators: {
//			toggleDownloadable: {
//				mode: 'manual',
//				label: 'Downloadable',
//				attributes: {
//					download: 'file'
//				}
//			}
//		}
//	},
//	placeholder: 'Type or paste your content here!',
//		simpleUpload: {
//	    uploadUrl: 'http://127.0.0.1:5000/posts/new-products-post',
//	    withCredentials: true,
//	    headers: {
//                'X-CSRF-TOKEN': 'CSRF-Token'
//        }
//	},
//	table: {
//		contentToolbar: ['tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties']
//	}
//};
//
//ClassicEditor.create(document.querySelector('#editor'), editorConfig);

