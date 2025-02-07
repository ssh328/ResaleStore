const {
	ClassicEditor,
	AutoImage,
	Autosave,
	BlockQuote,
	Bold,
	Code,
	Essentials,
	Heading,
	ImageBlock,
	ImageCaption,
	ImageInline,
	ImageInsert,
	ImageInsertViaUrl,
	ImageResize,
	ImageStyle,
	ImageTextAlternative,
	ImageToolbar,
	ImageUpload,
	Indent,
	IndentBlock,
	Italic,
	Link,
	LinkImage,
	Paragraph,
	SimpleUploadAdapter,
	SpecialCharacters,
	Strikethrough,
	Table,
	TableCaption,
	TableCellProperties,
	TableColumnResize,
	TableProperties,
	TableToolbar,
	Underline
} = window.CKEDITOR;

//const LICENSE_KEY =
//	'eyJhbGciOiJFUzI1NiJ9.eyJleHAiOjE3MzYwMzUxOTksImp0aSI6IjdhYTA3ZmUwLTM4NzQtNGE2My05YzFiLWQ4ZWQ0YTZkNDM3YyIsInVzYWdlRW5kcG9pbnQiOiJodHRwczovL3Byb3h5LWV2ZW50LmNrZWRpdG9yLmNvbSIsImRpc3RyaWJ1dGlvbkNoYW5uZWwiOlsiY2xvdWQiLCJkcnVwYWwiLCJzaCJdLCJ3aGl0ZUxhYmVsIjp0cnVlLCJsaWNlbnNlVHlwZSI6InRyaWFsIiwiZmVhdHVyZXMiOlsiKiJdLCJ2YyI6IjBlOTIyYWJhIn0.DXeaAofEs7YBz_iARES10HB9OhRtjNvUcb7BtTyOXD-oawJ0922tX2jxLImABOWKY3vgdZO3yOIlxyO8WtFWbQ';

const LICENSE_KEY =
	'eyJhbGciOiJFUzI1NiJ9.eyJleHAiOjE3MzY5ODU1OTksImp0aSI6ImI2MjQ1OTE3LTc3YTYtNDI5NS1hNGYxLWMzMWY2NTJmZTFiZCIsImxpY2Vuc2VkSG9zdHMiOlsiKi53ZWJjb250YWluZXIuaW8iLCIqLmpzaGVsbC5uZXQiLCIqLmNzcC5hcHAiLCJjZHBuLmlvIiwiMTI3LjAuMC4xIiwibG9jYWxob3N0IiwiMTkyLjE2OC4qLioiLCIxMC4qLiouKiIsIjE3Mi4qLiouKiIsIioudGVzdCIsIioubG9jYWxob3N0IiwiKi5sb2NhbCJdLCJkaXN0cmlidXRpb25DaGFubmVsIjpbImNsb3VkIiwiZHJ1cGFsIiwic2giXSwibGljZW5zZVR5cGUiOiJldmFsdWF0aW9uIiwidmMiOiI3MjdlN2M5YyJ9.mcMV1ojNhRR0sqpSxjIXYlZ1cf0Wotpno27hOZL0FC-4QD_r3nnb_-O1Y0fJXXxsfTU3XMlkFeKSFLvLOS9NLg';


const editorConfig = {
	toolbar: {
		items: [
			'heading',
			'|',
			'bold',
			'italic',
			'underline',
			'strikethrough',
			'code',
			'|',
			'specialCharacters',
			'link',
			'insertImage',
			'insertTable',
			'blockQuote',
			'|',
			'outdent',
			'indent'
		],
		shouldNotGroupWhenFull: false
	},
	plugins: [
		AutoImage,
		Autosave,
		BlockQuote,
		Bold,
		Code,
		Essentials,
		Heading,
		ImageBlock,
		ImageCaption,
		ImageInline,
		ImageInsert,
		ImageInsertViaUrl,
		ImageResize,
		ImageStyle,
		ImageTextAlternative,
		ImageToolbar,
		ImageUpload,
		Indent,
		IndentBlock,
		Italic,
		Link,
		LinkImage,
		Paragraph,
		SimpleUploadAdapter,
		SpecialCharacters,
		Strikethrough,
		Table,
		TableCaption,
		TableCellProperties,
		TableColumnResize,
		TableProperties,
		TableToolbar,
		Underline
	],
	heading: {
		options: [
			{
				model: 'paragraph',
				title: 'Paragraph',
				class: 'ck-heading_paragraph'
			},
			{
				model: 'heading1',
				view: 'h1',
				title: 'Heading 1',
				class: 'ck-heading_heading1'
			},
			{
				model: 'heading2',
				view: 'h2',
				title: 'Heading 2',
				class: 'ck-heading_heading2'
			},
			{
				model: 'heading3',
				view: 'h3',
				title: 'Heading 3',
				class: 'ck-heading_heading3'
			},
			{
				model: 'heading4',
				view: 'h4',
				title: 'Heading 4',
				class: 'ck-heading_heading4'
			},
			{
				model: 'heading5',
				view: 'h5',
				title: 'Heading 5',
				class: 'ck-heading_heading5'
			},
			{
				model: 'heading6',
				view: 'h6',
				title: 'Heading 6',
				class: 'ck-heading_heading6'
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
	language: 'ko',
	licenseKey: LICENSE_KEY,
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
	placeholder: 'Type or paste your content here!',
	simpleUpload: {
	    uploadUrl: '/posts/upload'
	},
	table: {
		contentToolbar: ['tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties']
	}
};

// ckeditor은 AJAX 방식을 사용하기 때문에 fetch를 사용해야함
ClassicEditor.create(document.querySelector('#editor'), editorConfig)
    .then(editor => { // 에디터가 성공적으로 초기화된 경우 실행
        // 에디터 데이터 가져오는 함수 정의

        const getEditorData = () => {
            return editor.getData(); // 현재 에디터 내용 HTML을 문자열로 반환
        };

        let currentImages = []; // 현재 이미지 리스트 저장 (URL 및 public_id 함께 저장)

        // 초기 데이터에서 이미지 정보 파싱
        const extractImageInfo = (data) => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            return Array.from(doc.querySelectorAll('img')).map(img => {
                const src = img.getAttribute('src'); // 이미지 URL

                // src 값이 없거나 null인 경우를 처리
                if (!src) {
                    console.warn('No src found for image');
                    return null; // 또는 원하는 처리 방식으로 변경 가능
                }

                console.log(src);

                const allowed_Extensions = ['png', 'jpg', 'jpeg', 'gif'];

                const fileExtension = src.split('.').pop().toLowerCase();

                let publicId = '';

                if (allowed_Extensions.includes(fileExtension)) {
                    const publicId_1 = src.split('Products/')[1]?.split('.' + fileExtension)[0];
                    const publicId = 'Products/' + publicId_1;

                    console.log(publicId);

                    return { src, publicId };
                } else {
                    console.log("Invalid file extension.");
                }

                if (!publicId) {
                    console.warn('No publicId found for image');
                    return null; // 또는 원하는 처리 방식으로 변경 가능
                }

            }).filter(item => item !== null); // null 값을 필터링하여 반환
        };

        // ckeditor가 초기화된 직후에 초기 데이터를 기반으로 currentImage를 초기화
        const initializeCurrentImages = () => {
            const editorData = getEditorData();
            currentImages = extractImageInfo(editorData); // 초기 이미지를 파싱하여 저장
            console.log('Initial images:', currentImages);
        };

        // 데이터가 변경될 때 실행
        editor.model.document.on('change:data', () => {
            const editorData = getEditorData();
            const newImages = extractImageInfo(editorData); // 새로운 이미지 리스트

            // 삭제된 이미지 계산
            const deletedImages = currentImages.filter(oldImg =>
                !newImages.some(newImg => newImg.src === oldImg.src)
            );

            // 서버에 삭제 요청
            deletedImages.forEach(({ publicId }) => {
                if (publicId) {
                    fetch('/posts/delete_image', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ public_id: publicId }),
                    })
                    .then(response => response.json())
                    .then(data => console.log('Deleted on server:', data))
                    .catch(error => console.error('Error deleting image:', error));
                }
            });

            currentImages = newImages; // 현재 이미지를 업데이트
        });

        initializeCurrentImages();

        // 저장 버튼 클릭 시 실행
        const saveButton = document.getElementById('saveButton')
        if (saveButton) {
            saveButton.addEventListener('click', function() {
                const editorData = getEditorData(); // 에디터에서 최신 데이터 가져오기

                // input의 title, price 값 추출
                const title = document.getElementById('title').value;
                const price = document.getElementById('price').value;
                const category = document.getElementById('category').value;

                // 데이터 전송
                fetch('/posts/save', { // '/save' 엔드포인트로 POST 요청
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json', // JSON 데이터 전송
                    },
                    body: JSON.stringify({ content: editorData, title: title, price: price, category: category })// 'content'라는 키로 데이터 전송
                })
                .then(response => response.json()) // 서버에서 응답을 받은 후, 응답을 JSON 형식으로 변환, 즉, 서버가 반환한 JSON 응답을 파싱
                .then(data => { // 파싱된 응답을 data로 받아옴. 이 데이터는 서버에서 보낸 JSON 객체
                                // 즉, 서버에서 jsonify({'redirect': ...})로 반환된 JSON 응답을 클라이언트에서 .then(data => {...}) 부분에서 처리
                    if (data.redirect) {    // 서버에서 반환된 data 객체에 redirect 키가 존재하는지 확인
                        window.location.href = data.redirect;   // 클라이언트 브라우저를 다른 페이지로 리디렉션 시킴
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        }

        const editButton = document.getElementById('editButton')
        if (editButton) {
            editButton.addEventListener('click', function() {
                const editorData = getEditorData(); // 에디터에서 최신 데이터 가져오기

                // input의 title, price 값 추출
                const title = document.getElementById('title').value;
                const price = document.getElementById('price').value;

                const currentPath = window.location.pathname;
                const postId = currentPath.split('/').pop();

                // 데이터 전송
                fetch('/posts/edit_save', { // '/save' 엔드포인트로 POST 요청
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json', // JSON 데이터 전송
                    },
                    body: JSON.stringify({ content: editorData, title: title, price: price, post_id: postId })// 'content'라는 키로 데이터 전송
                })
                .then(response => response.json()) // 서버에서 응답을 받은 후, 응답을 JSON 형식으로 변환, 즉, 서버가 반환한 JSON 응답을 파싱
                .then(data => { // 파싱된 응답을 data로 받아옴. 이 데이터는 서버에서 보낸 JSON 객체
                                // 즉, 서버에서 jsonify({'redirect': ...})로 반환된 JSON 응답을 클라이언트에서 .then(data => {...}) 부분에서 처리
                    if (data.redirect) {    // 서버에서 반환된 data 객체에 redirect 키가 존재하는지 확인
                        window.location.href = data.redirect;   // 클라이언트 브라우저를 다른 페이지로 리디렉션 시킴
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        }


    })
    .catch(error => {
        console.error('Editor initialization error:', error);   // 에디터 초기화 실패 시 에러 출력
    });