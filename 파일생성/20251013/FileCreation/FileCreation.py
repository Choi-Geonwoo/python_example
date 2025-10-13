import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from pathlib import Path

# -------------------------
# 템플릿 렌더링 함수
# -------------------------
def render_template(template_path, context):
    template_file_path = Path("templates") / template_path
    if not template_file_path.exists():
        raise FileNotFoundError(f"템플릿 파일이 없습니다: {template_file_path}")

    with open(template_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    for key, value in context.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content

# -------------------------
# 파일 생성 함수
# -------------------------
def generate_files(base_path_input, folder_name, process_name):
    folders = {
        "controller": "controller.template",
        "service": "service.template",
        "serviceimpl": "serviceimpl.template",
        "mapper": "mapper.template",
        "xml": "xml.template"
    }

    base_path = Path(base_path_input)
    target_path = base_path / folder_name

    try:
        src_index = base_path.parts.index("src")
        project_root = Path(*base_path.parts[:src_index])
    except ValueError:
        project_root = base_path.parents[3]

    resources_mapper_path = project_root / "src" / "main" / "resources" / "mapper"

    try:
        java_index = base_path.parts.index("java")
        package_base = ".".join(base_path.parts[java_index + 1:])
        if not package_base:
            package_base = "com.example"
    except ValueError:
        package_base = "com.example.app"

    for dir_name, template_file in folders.items():
        if dir_name == "serviceimpl":
            dir_path = target_path / "service/impl"
            package_name = f"{package_base}.{folder_name}.service.impl"
        elif dir_name == "service":
            dir_path = target_path / dir_name
            package_name = f"{package_base}.{folder_name}.service"
        elif dir_name == "xml":
            dir_path = resources_mapper_path / folder_name
            package_name =  f"{package_base}.{folder_name}.Mapper"
        else:
            dir_path = target_path / dir_name
            package_name = f"{package_base}.{folder_name}.{dir_name}"

        dir_path.mkdir(parents=True, exist_ok=True)

        if dir_name == "service":
            class_name = f"{folder_name}Service"
        elif dir_name == "serviceimpl":
            class_name = f"{folder_name}ServiceImpl"
        elif dir_name == "mapper":
            class_name = f"{folder_name}Mapper"
        else:
            class_name = f"{folder_name}{dir_name.title()}"

        service_class_name = f"{folder_name}Service"
        service_var_name = f"{folder_name[0].lower()}{folder_name[1:]}Service"
        mapper_class_name = f"{folder_name}Mapper"
        mapper_var_name = f"{folder_name[0].lower()}{folder_name[1:]}Mapper"

        if dir_name == "xml":
            class_name = f"{folder_name}Mapper"
            file_path = dir_path / f"{class_name}.xml"
        else:
            file_path = dir_path / f"{class_name}.java"

        context = {
            "package_name": package_name,
            "class_name": class_name,
            "folder_name": folder_name,
            "folder_name_lower": folder_name,
            "package_base": package_base,
            "process_name": process_name,
            "service_class_name": service_class_name,
            "service_var_name": service_var_name,
            "interface_class_name": service_class_name,
            "mapper_class_name": mapper_class_name,
            "mapper_var_name": mapper_var_name
        }

        content = render_template(template_file, context)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

# -------------------------
# PyQt6 GUI 클래스
# -------------------------
class FileGeneratorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Java 파일 생성기")
        self.setGeometry(100, 100, 500, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- 기본 경로 ---
        hbox1 = QHBoxLayout()
        lbl_base = QLabel("기본 경로:".ljust(23))
        self.txt_base = QLineEdit()
        btn_browse = QPushButton("찾아보기")
        btn_browse.clicked.connect(self.browse_folder)
        hbox1.addWidget(lbl_base)
        hbox1.addWidget(self.txt_base)
        hbox1.addWidget(btn_browse)

        # --- 폴더 이름 ---
        hbox2 = QHBoxLayout()
        lbl_folder = QLabel("생성할 폴더 이름:".ljust(18))
        self.txt_folder = QLineEdit()
        hbox2.addWidget(lbl_folder)
        hbox2.addWidget(self.txt_folder)

        # --- 프로세스명 ---
        hbox3 = QHBoxLayout()
        lbl_process = QLabel("프로세스명:".ljust(23))
        self.txt_process = QLineEdit()
        hbox3.addWidget(lbl_process)
        hbox3.addWidget(self.txt_process)

        # --- 생성 버튼 ---
        self.btn_generate = QPushButton("파일 생성")
        self.btn_generate.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; height: 35px;")
        self.btn_generate.clicked.connect(self.on_generate)

        # --- 레이아웃 조합 ---
        layout.addLayout(hbox1)
        layout.addLayout(hbox2)
        layout.addLayout(hbox3)
        layout.addWidget(self.btn_generate)

        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "폴더 선택")
        if folder:
            self.txt_base.setText(folder)

    def on_generate(self):
        base = self.txt_base.text().strip()
        folder = self.txt_folder.text().strip()
        process = self.txt_process.text().strip()

        if not base or not folder or not process:
            QMessageBox.warning(self, "경고", "모든 항목을 입력하세요.")
            return

        try:
            generate_files(base, folder, process)
            QMessageBox.information(self, "완료", "파일 생성이 완료되었습니다!")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일 생성 중 오류 발생:\n{e}")

# -------------------------
# 앱 실행
# -------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = FileGeneratorGUI()
    gui.show()
    sys.exit(app.exec())
