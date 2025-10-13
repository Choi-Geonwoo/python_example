import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re

class JavaFileGenerator(tk.Tk):
    """
    Tkinter를 사용한 Java 파일 구조 자동 생성 GUI 애플리케이션
    (Java CRUD 및 MyBatis XML 템플릿 포함, HTML 제외)
    """
    def __init__(self):
        super().__init__()
        self.title("Java 파일 구조 자동 생성기 (CRUD 및 XML)")
        self.geometry("750x650") # 창 크기 조정
        self.configure(bg='#f0f0f0')

        # 스타일 설정
        self.option_add('*Font', 'MalgunGothic 10')
        self.option_add('*Label.Font', 'MalgunGothic 10 bold')

        self.create_widgets()

    def create_widgets(self):
        # 메인 프레임 설정
        main_frame = tk.Frame(self, bg='#f0f0f0', padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)

        # 1. 기본 경로 입력 섹션
        path_frame = tk.LabelFrame(main_frame, text="1. 기본 경로 설정 (Java 패키지 루트까지, 예: .../src/main/java/com/example)", bg='white', padx=10, pady=10)
        path_frame.pack(fill='x', pady=10)

        tk.Label(path_frame, text="기본 경로:", bg='white').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.base_path_var = tk.StringVar(value=r"C:")
        tk.Entry(path_frame, textvariable=self.base_path_var, width=60).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(path_frame, text="폴더 선택", command=self.browse_path).grid(row=0, column=2, padx=5, pady=5)

        # 2. 모듈명 입력 섹션
        module_frame = tk.LabelFrame(main_frame, text="2. 모듈 정보 입력", bg='white', padx=10, pady=10)
        module_frame.pack(fill='x', pady=10)

        tk.Label(module_frame, text="모듈명 (예: bank):", bg='white').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.module_name_var = tk.StringVar(value="")
        tk.Entry(module_frame, textvariable=self.module_name_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        
        # 3. 실행 버튼
        tk.Button(main_frame, text="3. 파일 구조 생성 실행 (Java 4개, XML 1개만 생성)", 
                  command=self.execute_generation, 
                  bg='#4CAF50', fg='white', relief='raised', 
                  font='MalgunGothic 12 bold', padx=10, pady=5).pack(fill='x', pady=15)

        # 4. 결과 출력 섹션
        result_frame = tk.LabelFrame(main_frame, text="4. 실행 로그", bg='white', padx=10, pady=5)
        result_frame.pack(fill='both', expand=True)

        self.log_text = tk.Text(result_frame, wrap='word', height=15, bg='#333333', fg='white', insertbackground='white')
        self.log_text.pack(fill='both', expand=True)

    def browse_path(self):
        """파일 시스템에서 디렉토리를 선택하는 함수"""
        directory = filedialog.askdirectory(title="기본 경로 선택")
        if directory:
            self.base_path_var.set(directory)

    def log_message(self, message):
        """로그 텍스트 영역에 메시지를 출력하는 함수"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) # 스크롤을 맨 아래로 이동

    def deduce_package_name(self, base_path):
        """기본 경로에서 Java 패키지 이름을 추론하는 함수"""
        path = base_path.replace('\\', '/')
        match = re.search(r'(?:src/main/java/)(.*)', path)
        
        if match:
            package_path = match.group(1)
        else:
            # src/main/java가 없는 경우, 전체 경로의 마지막 부분을 사용 
            package_path = path.split('/')[-1]

        # 경로 구분자를 .으로 변경하여 패키지 이름 생성
        package_name = package_path.replace('/', '.')
        return package_name.strip('.')

    def deduce_resource_base_path(self, java_base_path):
        """Java 경로에서 src/main/resources 경로를 추론하는 함수"""
        path = java_base_path.replace('\\', '/')
        # 'src/main/java' 부분을 'src/main/resources'로 대체
        if 'src/main/java' in path:
            # 'src/main/java'의 시작점까지만 추출하고 'src/main/resources'를 붙임
            return path.split('src/main/java')[0] + 'src/main/resources'
        
        # Fallback: 대체가 안 되면 현재 경로를 기본으로 간주 (사용자가 정확히 경로를 입력해야 함)
        return os.path.join(java_base_path, '..', '..', 'resources')


    def get_crud_template(self, class_name, file_type):
        """클래스 타입에 따른 CRUD 함수 템플릿을 생성합니다. (사용자 정의 함수명 적용)"""
        
        entity_name = class_name + "Entity"
        lower_class_name = class_name.lower()
        
        # Mapper 인터페이스 템플릿
        if file_type == 'Mapper':
            # Mapper는 XML ID와의 일치를 위해 selectList{class_name}와 insert{class_name}을 사용
            return f"""
    // C: 데이터 삽입 (Mapper Method: insert{class_name} 사용)
    int insert{class_name}({entity_name} {lower_class_name});

    // R: 단일 데이터 조회
    {entity_name} selectOne{class_name}(int id); 

    // R: 목록 데이터 조회
    List<{entity_name}> selectList{class_name}();

    // U: 데이터 수정 (사용자 정의 Mapper Method: {class_name}Update 사용)
    int {class_name}Update({entity_name} {lower_class_name});

    // D: 데이터 삭제
    int delete{class_name}(int id);
"""
        # Service 인터페이스 템플릿
        elif file_type == 'Service':
            # Service Layer는 사용자 정의 함수명 사용
            return f"""
    // C: 데이터 삽입
    int {class_name}Save({entity_name} {lower_class_name});

    // R: 단일 데이터 조회
    {entity_name} {class_name}Get(int id);

    // R: 목록 데이터 조회 (사용자 정의 Service Method: {class_name}GetSelete 사용)
    List<{entity_name}> {class_name}GetSelete();

    // U: 데이터 수정
    int {class_name}Update({entity_name} {lower_class_name});

    // D: 데이터 삭제
    int delete{class_name}(int id);
"""
        # ServiceImpl 구현체 템플릿
        elif file_type == 'ServiceImpl':
            mapper_name = class_name + "Mapper"
            lower_mapper_name = mapper_name.lower()

            return f"""
    @Autowired
    private {mapper_name} {lower_mapper_name};
    
    // C: 데이터 삽입 (Service Method: {class_name}Save -> Mapper Method: insert{class_name})
    @Override
    public int {class_name}Save({entity_name} {lower_class_name}) {{
        return {lower_mapper_name}.insert{class_name}({lower_class_name});
    }}

    // R: 단일 데이터 조회
    @Override
    public {entity_name} {class_name}Get(int id) {{
        return {lower_mapper_name}.selectOne{class_name}(id);
    }}

    // R: 목록 데이터 조회 (Service Method: {class_name}GetSelete -> Mapper Method: selectList{class_name})
    @Override
    public List<{entity_name}> {class_name}GetSelete() {{
        return {lower_mapper_name}.selectList{class_name}();
    }}

    // U: 데이터 수정 (Service Method: {class_name}Update -> Mapper Method: {class_name}Update)
    @Override
    public int {class_name}Update({entity_name} {lower_class_name}) {{
        return {lower_mapper_name}.{class_name}Update({lower_class_name});
    }}

    // D: 데이터 삭제
    @Override
    public int delete{class_name}(int id) {{
        return {lower_mapper_name}.delete{class_name}(id);
    }}
"""
        return "// TODO: Add methods here"

    def get_html_template(self, class_name):
        """HTML 내용 없이 빈 파일 생성"""
        return ""  # 빈 파일
    
    def get_xml_template(self, class_name, namespace):
        """MyBatis Mapper XML 템플릿 (CRUD 포함)을 생성합니다. (사용자 정의 함수명 적용)"""
        lower_class_name = class_name.lower()
        entity_name = class_name + "Entity"
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<!-- namespace는 {class_name}Mapper 인터페이스의 풀 패키지 경로와 일치해야 합니다. -->
<mapper namespace="{namespace}">

    <!-- C: 데이터 삽입 (Mapper Method: insert{class_name}) -->
    <insert id="insert{class_name}" parameterType="{entity_name}" useGeneratedKeys="true" keyProperty="id">
        /* {namespace}.insert{class_name} */
        INSERT INTO {lower_class_name}_tb (
            field1, field2, reg_date
        ) VALUES (
            #{{{lower_class_name}.field1}},
            #{{{lower_class_name}.field2}},
            NOW()
        )
    </insert>

    <!-- R: 단일 데이터 조회 (Mapper Method: selectOne{class_name}) -->
    <select id="selectOne{class_name}" parameterType="int" resultType="{entity_name}">
        /* {namespace}.selectOne{class_name} */
        SELECT 
            id, field1, field2, reg_date
        FROM 
            {lower_class_name}_tb
        WHERE 
            id = #{{id}}
    </select>
    
    <!-- R: 목록 조회 (Mapper Method: selectList{class_name}) -->
    <select id="selectList{class_name}" resultType="{entity_name}">
        /* {namespace}.selectList{class_name} */
        SELECT 
            id, field1, field2, reg_date
        FROM 
            {lower_class_name}_tb
        ORDER BY 
            reg_date DESC
    </select>

    <!-- U: 데이터 수정 (Mapper Method: {class_name}Update) -->
    <update id="{class_name}Update" parameterType="{entity_name}">
        /* {namespace}.{class_name}Update */
        UPDATE {lower_class_name}_tb
        SET
            field1 = #{{{lower_class_name}.field1}},
            field2 = #{{{lower_class_name}.field2}},
            mod_date = NOW()
        WHERE
            id = #{{{lower_class_name}.id}}
    </update>
    
    <!-- D: 데이터 삭제 (Mapper Method: delete{class_name}) -->
    <delete id="delete{class_name}" parameterType="int">
        /* {namespace}.delete{class_name} */
        DELETE FROM {lower_class_name}_tb
        WHERE id = #{{id}}
    </delete>

</mapper>
"""

    def execute_generation(self):
        """파일 생성 로직을 실행하는 메인 함수"""
        self.log_text.delete('1.0', tk.END)
        
        java_base_path = self.base_path_var.get().strip()
        module_name_input = self.module_name_var.get().strip()

        if not java_base_path or not module_name_input:
            messagebox.showerror("입력 오류", "기본 경로와 모듈명을 모두 입력해 주세요.")
            return
        
        class_name = module_name_input.capitalize()
        lower_module_name = module_name_input.lower()
        entity_name = class_name + "Entity"

        # 1. 경로 추론
        base_package = self.deduce_package_name(java_base_path)
        resource_base_path = self.deduce_resource_base_path(java_base_path)

        self.log_message(f"--- 파일 생성 작업 시작 ---")
        self.log_message(f"Java Base: {java_base_path}")
        self.log_message(f"Resource Base (추론): {resource_base_path}")
        self.log_message(f"기본 패키지: {base_package}")

        # 2. 생성할 파일 목록 정의
        
        # A. Java 파일 (총 4개)
        java_files_to_create = [
            ('controller', 'Controller', 'Controller'),
            ('mapper', 'Mapper', 'Mapper Interface'),
            ('service', 'Service', 'Service Interface'),
            ('service', 'ServiceImpl', 'Service Implementation')
        ]
        
        # B. Resource 파일 (XML 1개만 남김)
        resource_files_to_create = [
            ('templates', f'{lower_module_name}_list.html', 'HTML View'),  # HTML
            ('mapper', f'{class_name}Mapper.xml', 'MyBatis Mapper XML')
        ]

        # 3. Java 파일 생성
        for subdir, file_type, type_desc in java_files_to_create:
            is_interface = 'Interface' in type_desc
            filename = f'{class_name}{file_type}.java'
            
            target_dir = os.path.join(java_base_path, class_name, subdir)
            full_path = os.path.join(target_dir, filename)
            
            try:
                os.makedirs(target_dir, exist_ok=True)
            except OSError as e:
                self.log_message(f"❌ 오류: Java 디렉토리 생성 실패 ({target_dir}): {e}")
                continue

            final_package_name = f"{base_package}.{lower_module_name}.{subdir}"
            annotation = ''
            if file_type == 'Controller': annotation = '@RestController'
            elif file_type == 'ServiceImpl': annotation = '@Service'
            elif file_type == 'Mapper': annotation = '@Mapper'

            crud_template = self.get_crud_template(class_name, file_type)
            
            imports = ''
            if file_type in ['Mapper', 'Service', 'ServiceImpl']: imports += 'import java.util.List;\n'
            if file_type == 'ServiceImpl': imports += 'import org.springframework.beans.factory.annotation.Autowired;\nimport org.springframework.stereotype.Service;\n'
            if file_type == 'Mapper': imports += 'import org.apache.ibatis.annotations.Mapper;\n'
            
            # Controller 템플릿 재구성 (이전과 동일한 사용자 정의 로직 유지)
            if file_type == 'Controller':
                imports += 'import org.springframework.beans.factory.annotation.Autowired;\n'
                imports += 'import org.springframework.web.bind.annotation.*;\n'
                imports += f'import {base_package}.{lower_module_name}.service.{class_name}Service;\n'
                crud_template = f"""
    @Autowired
    private {class_name}Service {lower_module_name}Service;

    /**
    * @methodName    : {class_name}GetSelete
    * @author        : Jihun Park
    * @date          : 
    * @return        :  List<{entity_name}>
    * @description   : {class_name} 목록 조회
    */
    @GetMapping("/list")
    public List<{entity_name}> {class_name}GetSelete() {{
        return {lower_module_name}Service.{class_name}GetSelete();
    }}
    
    /**
    * @methodName    : {class_name}Get
    * @author        : Jihun Park
    * @date          : 
    * @return        : {entity_name}
    * @description   : {class_name} 등록
    */
    @GetMapping("/{lower_module_name}/{{id}}")
    public {entity_name} {class_name}Get(@PathVariable int id) {{
        return {lower_module_name}Service.{class_name}Get(id);
    }}

    /**
    * @methodName    : {class_name}Save
    * @author        : Jihun Park
    * @date          : 
    * @return        : int
    * @description   :  {class_name} 등록
    */
    @PostMapping("/{lower_module_name}/save")
    public int {class_name}Save(@RequestBody {entity_name} {lower_module_name}Entity) {{
        return {lower_module_name}Service.{class_name}Save({lower_module_name}Entity);
    }}
    
    /**
    * @methodName    : {class_name}Update
    * @author        : Jihun Park
    * @date          : 
    * @return        : int
    * @description   : {class_name} 수정
    */
    @PostMapping("/{lower_module_name}/update")
    public int {class_name}Update(@RequestBody {entity_name} {lower_module_name}Entity) {{
        return {lower_module_name}Service.{class_name}Update({lower_module_name}Entity);
    }}
    
    /**
    * @methodName    : delete{class_name}
    * @author        : Jihun Park
    * @date          : 2024.09.16
    * @return        : int
    * @description   : {class_name} 삭제
    */
    @DeleteMapping("/{lower_module_name}/{{id}}")
    public int delete{class_name}(@PathVariable int id) {{  
        return {lower_module_name}Service.delete{class_name}(id);
    }}
"""

            file_content = f"""package {final_package_name};

{imports}
/**
 * {type_desc}: {class_name} {file_type}
 * 대상 엔티티: {entity_name} (임의로 가정된 이름)
 */
{annotation}
public {'interface' if is_interface else 'class'} {filename.split('.')[0]} {'implements ' + class_name + 'Service' if file_type == 'ServiceImpl' else ''} {{
{crud_template}
}}
"""
            try:
                with open(full_path, 'w', encoding='utf-8') as f: f.write(file_content)
                self.log_message(f"✅ [Java] 생성 성공: {full_path}")
            except IOError as e:
                self.log_message(f"❌ [Java] 오류: 파일 쓰기 실패 ({full_path}): {e}")


        # 4. Resource 파일 생성 (XML만)
        for sub_path, filename, file_type in resource_files_to_create:
            
            # HTML: /templates/{module_name}/ 
            if sub_path == 'templates': 
                target_dir = os.path.join(resource_base_path, sub_path, lower_module_name) 
                content = self.get_html_template(class_name) 
            # # XML: /mapper/{module_name}/ 
            elif sub_path == 'mapper':
                target_dir = os.path.join(resource_base_path, sub_path, lower_module_name)
                mapper_namespace = f"{base_package}.{lower_module_name}.mapper.{class_name}Mapper"
                content = self.get_xml_template(class_name, mapper_namespace)

            full_path = os.path.join(target_dir, filename)

            try:
                os.makedirs(target_dir, exist_ok=True)
            except OSError as e:
                self.log_message(f"❌ 오류: Resource 디렉토리 생성 실패 ({target_dir}): {e}")
                continue

            try:
                with open(full_path, 'w', encoding='utf-8') as f: f.write(content)
                self.log_message(f"✅ [{file_type}] 생성 성공: {full_path}")
            except IOError as e:
                self.log_message(f"❌ [{file_type}] 오류: 파일 쓰기 실패 ({full_path}): {e}")
                
        self.log_message(f"--- 파일 생성 작업 완료 (총 6개 파일: Java 4개, XML 1개, HTML 1개) ---")
        messagebox.showinfo("완료", "Java 및 MyBatis XML 파일 구조 생성이 완료되었습니다.\n로그를 확인해 주세요.")

if __name__ == "__main__":
    app = JavaFileGenerator()
    app.mainloop()
