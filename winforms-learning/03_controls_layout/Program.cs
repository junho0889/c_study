// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WinForms 03 - 컨트롤과 레이아웃 (Controls & Layout)    ■
// ■  학생 등록 폼 만들기                                     ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
//
// 이 파일에서 배우는 것:
//   1) TextBox       - 글자를 입력하는 칸 (학교 시험지의 이름 쓰는 칸)
//   2) ComboBox      - 드롭다운 목록 (자판기에서 음료 고르기)
//   3) ListBox       - 여러 항목을 보여주는 목록 (출석부)
//   4) RadioButton   - 하나만 고르는 동그라미 (객관식 한 개 선택)
//   5) CheckBox      - 여러 개 고를 수 있는 네모 (쇼핑 체크리스트)
//   6) GroupBox      - 관련 항목을 묶는 테두리 상자 (필통 안에 연필끼리)
//   7) Panel         - 보이지 않는 그릇 (서랍 칸막이)
//   8) FlowLayoutPanel - 자동으로 줄 바꿈 하는 판 (책꽂이에 책 꽂기)
//   9) TableLayoutPanel - 표처럼 배치하는 판 (바둑판)
//  10) Dock / Anchor - 창 크기가 변할 때 컨트롤 위치를 고정하는 방법

using System;
using System.Drawing;
using System.Windows.Forms;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new StudentRegistrationForm());
    }
}

// ┌──────────────────────────────────────────────────┐
// │  학생 등록 폼 - 모든 컨트롤을 한 화면에 배치      │
// └──────────────────────────────────────────────────┘
public sealed class StudentRegistrationForm : Form
{
    // ── 입력 컨트롤들 ──
    private readonly TextBox _nameTextBox;
    private readonly TextBox _ageTextBox;
    private readonly ComboBox _gradeComboBox;
    private readonly RadioButton _radioMale;
    private readonly RadioButton _radioFemale;
    private readonly CheckBox _chkMath;
    private readonly CheckBox _chkScience;
    private readonly CheckBox _chkEnglish;
    private readonly CheckBox _chkArt;
    private readonly ListBox _studentListBox;
    private readonly Label _statusLabel;

    public StudentRegistrationForm()
    {
        // ┌──────────────────────────────────────────┐
        // │  1단계: 폼(창) 기본 설정                   │
        // └──────────────────────────────────────────┘
        // 폼은 도화지입니다. 크기와 제목을 먼저 정합니다.
        Text = "학생 등록 시스템 - WinForms 컨트롤 학습";
        Size = new Size(800, 620);
        StartPosition = FormStartPosition.CenterScreen;
        MinimumSize = new Size(700, 500); // 창을 너무 작게 줄이지 못하게

        // ┌──────────────────────────────────────────┐
        // │  2단계: TableLayoutPanel - 바둑판 배치     │
        // └──────────────────────────────────────────┘
        // TableLayoutPanel은 바둑판처럼 행(가로줄)과 열(세로줄)을 만들어
        // 각 칸에 컨트롤을 하나씩 넣는 방식입니다.
        // 엑셀 시트에 한 칸에 하나씩 글을 쓰는 것과 같아요!
        var mainTable = new TableLayoutPanel
        {
            Dock = DockStyle.Fill, // Dock.Fill = 폼 전체를 꽉 채움 (벽지를 벽에 붙이듯)
            ColumnCount = 2,
            RowCount = 1,
            Padding = new Padding(10)
        };
        // 왼쪽 열 60%, 오른쪽 열 40%
        mainTable.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 60F));
        mainTable.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 40F));

        // ┌──────────────────────────────────────────┐
        // │  3단계: 왼쪽 패널 - 입력 영역              │
        // └──────────────────────────────────────────┘
        // Panel은 투명한 서랍입니다. 여러 컨트롤을 담아서 한꺼번에 옮길 수 있어요.
        var leftPanel = new Panel
        {
            Dock = DockStyle.Fill,
            AutoScroll = true // 내용이 많으면 스크롤바가 자동으로 나타남
        };

        int y = 10; // y좌표: 위에서 아래로 내려가며 컨트롤을 배치

        // ── 이름 입력 ──
        // Label은 이름표입니다. "여기에 이름을 쓰세요"라고 알려주는 역할이에요.
        leftPanel.Controls.Add(new Label
        {
            Text = "이름:",
            Location = new Point(10, y),
            AutoSize = true,
            Font = new Font("맑은 고딕", 10, FontStyle.Bold)
        });
        y += 25;

        // TextBox는 글자를 입력하는 빈 칸입니다.
        // 시험지에서 "이름: ________" 부분의 밑줄과 같아요.
        _nameTextBox = new TextBox
        {
            Location = new Point(10, y),
            Size = new Size(250, 28),
            Font = new Font("맑은 고딕", 10),
            PlaceholderText = "학생 이름을 입력하세요" // 힌트 텍스트
        };
        leftPanel.Controls.Add(_nameTextBox);
        y += 40;

        // ── 나이 입력 ──
        leftPanel.Controls.Add(new Label
        {
            Text = "나이:",
            Location = new Point(10, y),
            AutoSize = true,
            Font = new Font("맑은 고딕", 10, FontStyle.Bold)
        });
        y += 25;

        _ageTextBox = new TextBox
        {
            Location = new Point(10, y),
            Size = new Size(100, 28),
            Font = new Font("맑은 고딕", 10),
            PlaceholderText = "숫자만"
        };
        // 나이 칸에는 숫자만 입력할 수 있게 제한합니다.
        // KeyPress 이벤트: 키보드를 누를 때마다 발생하는 신호
        _ageTextBox.KeyPress += (s, e) =>
        {
            // Char.IsDigit = 숫자인지 확인, IsControl = 백스페이스 등 특수키
            if (!char.IsDigit(e.KeyChar) && !char.IsControl(e.KeyChar))
                e.Handled = true; // true로 하면 입력이 무시됨 (문지기가 막는 것)
        };
        leftPanel.Controls.Add(_ageTextBox);
        y += 40;

        // ┌──────────────────────────────────────────┐
        // │  4단계: ComboBox - 드롭다운 목록           │
        // └──────────────────────────────────────────┘
        // ComboBox는 자판기처럼 목록 중 하나를 고르는 컨트롤입니다.
        // 화살표를 누르면 선택지가 펼쳐집니다.
        leftPanel.Controls.Add(new Label
        {
            Text = "학년:",
            Location = new Point(10, y),
            AutoSize = true,
            Font = new Font("맑은 고딕", 10, FontStyle.Bold)
        });
        y += 25;

        _gradeComboBox = new ComboBox
        {
            Location = new Point(10, y),
            Size = new Size(150, 28),
            Font = new Font("맑은 고딕", 10),
            DropDownStyle = ComboBoxStyle.DropDownList // 직접 입력 불가, 선택만 가능
        };
        // Items.AddRange로 여러 항목을 한 번에 추가합니다.
        _gradeComboBox.Items.AddRange(new object[]
        {
            "1학년", "2학년", "3학년", "4학년", "5학년", "6학년"
        });
        _gradeComboBox.SelectedIndex = 0; // 첫 번째 항목을 기본 선택
        leftPanel.Controls.Add(_gradeComboBox);
        y += 40;

        // ┌──────────────────────────────────────────┐
        // │  5단계: GroupBox + RadioButton             │
        // └──────────────────────────────────────────┘
        // GroupBox는 관련된 것들을 하나로 묶어주는 테두리 상자입니다.
        // 필통 안에 연필끼리, 지우개끼리 칸을 나누는 것과 같아요.
        //
        // RadioButton은 객관식 문제처럼 하나만 선택할 수 있습니다.
        // 같은 GroupBox 안의 RadioButton끼리 하나만 선택됩니다.
        var genderGroup = new GroupBox
        {
            Text = "성별",
            Location = new Point(10, y),
            Size = new Size(250, 60),
            Font = new Font("맑은 고딕", 10, FontStyle.Bold)
        };

        _radioMale = new RadioButton
        {
            Text = "남자",
            Location = new Point(15, 25),
            AutoSize = true,
            Checked = true, // 기본 선택
            Font = new Font("맑은 고딕", 9, FontStyle.Regular)
        };

        _radioFemale = new RadioButton
        {
            Text = "여자",
            Location = new Point(100, 25),
            AutoSize = true,
            Font = new Font("맑은 고딕", 9, FontStyle.Regular)
        };

        genderGroup.Controls.Add(_radioMale);
        genderGroup.Controls.Add(_radioFemale);
        leftPanel.Controls.Add(genderGroup);
        y += 70;

        // ┌──────────────────────────────────────────┐
        // │  6단계: CheckBox - 다중 선택               │
        // └──────────────────────────────────────────┘
        // CheckBox는 쇼핑 체크리스트처럼 여러 개를 동시에 체크할 수 있습니다.
        // RadioButton과 다른 점: RadioButton은 하나만, CheckBox는 여러 개!
        var subjectGroup = new GroupBox
        {
            Text = "수강 과목 (여러 개 선택 가능)",
            Location = new Point(10, y),
            Size = new Size(250, 70),
            Font = new Font("맑은 고딕", 10, FontStyle.Bold)
        };

        // FlowLayoutPanel을 GroupBox 안에 넣으면
        // CheckBox들이 자동으로 가로로 나열됩니다.
        // 책꽂이에 책을 꽂으면 자동으로 옆으로 밀리는 것처럼!
        var subjectFlow = new FlowLayoutPanel
        {
            Dock = DockStyle.Fill,
            Padding = new Padding(5)
        };

        _chkMath = new CheckBox { Text = "수학", AutoSize = true, Font = new Font("맑은 고딕", 9) };
        _chkScience = new CheckBox { Text = "과학", AutoSize = true, Font = new Font("맑은 고딕", 9) };
        _chkEnglish = new CheckBox { Text = "영어", AutoSize = true, Font = new Font("맑은 고딕", 9) };
        _chkArt = new CheckBox { Text = "미술", AutoSize = true, Font = new Font("맑은 고딕", 9) };

        subjectFlow.Controls.Add(_chkMath);
        subjectFlow.Controls.Add(_chkScience);
        subjectFlow.Controls.Add(_chkEnglish);
        subjectFlow.Controls.Add(_chkArt);
        subjectGroup.Controls.Add(subjectFlow);
        leftPanel.Controls.Add(subjectGroup);
        y += 80;

        // ┌──────────────────────────────────────────┐
        // │  7단계: 등록 버튼                          │
        // └──────────────────────────────────────────┘
        var registerButton = new Button
        {
            Text = "등록하기",
            Location = new Point(10, y),
            Size = new Size(250, 40),
            Font = new Font("맑은 고딕", 11, FontStyle.Bold),
            BackColor = Color.RoyalBlue,
            ForeColor = Color.White,
            FlatStyle = FlatStyle.Flat
        };
        registerButton.Click += RegisterButton_Click;
        leftPanel.Controls.Add(registerButton);

        // ┌──────────────────────────────────────────┐
        // │  8단계: 오른쪽 - ListBox (출석부)          │
        // └──────────────────────────────────────────┘
        // ListBox는 등록된 학생 목록을 보여줍니다.
        // 학교 출석부에 이름이 한 줄씩 적히는 것과 같아요!
        var rightPanel = new Panel { Dock = DockStyle.Fill };

        rightPanel.Controls.Add(new Label
        {
            Text = "등록된 학생 목록",
            Dock = DockStyle.Top,
            Height = 30,
            Font = new Font("맑은 고딕", 11, FontStyle.Bold),
            TextAlign = ContentAlignment.MiddleLeft
        });

        _studentListBox = new ListBox
        {
            Dock = DockStyle.Fill, // 남은 공간을 꽉 채움
            Font = new Font("맑은 고딕", 10),
            IntegralHeight = false
        };
        rightPanel.Controls.Add(_studentListBox);

        // ── 상태 표시줄 ──
        // Anchor는 닻(배를 고정하는 닻)처럼 컨트롤의 위치를 고정합니다.
        // Anchor = Bottom | Left | Right → 창 아래쪽에 고정, 좌우로 늘어남
        _statusLabel = new Label
        {
            Text = "학생을 등록해 보세요!",
            Dock = DockStyle.Bottom,
            Height = 30,
            Font = new Font("맑은 고딕", 9),
            TextAlign = ContentAlignment.MiddleLeft,
            BackColor = Color.LightYellow,
            BorderStyle = BorderStyle.FixedSingle
        };
        rightPanel.Controls.Add(_statusLabel);

        // ┌──────────────────────────────────────────┐
        // │  9단계: 테이블에 패널 배치                  │
        // └──────────────────────────────────────────┘
        mainTable.Controls.Add(leftPanel, 0, 0);   // (열0, 행0) = 왼쪽
        mainTable.Controls.Add(rightPanel, 1, 0);   // (열1, 행0) = 오른쪽
        Controls.Add(mainTable);
    }

    // ┌──────────────────────────────────────────┐
    // │  등록 버튼 클릭 이벤트 처리                │
    // └──────────────────────────────────────────┘
    private void RegisterButton_Click(object? sender, EventArgs e)
    {
        // 입력값 검증 - 이름이 비어있으면 등록 불가
        if (string.IsNullOrWhiteSpace(_nameTextBox.Text))
        {
            MessageBox.Show("이름을 입력하세요!", "알림",
                MessageBoxButtons.OK, MessageBoxIcon.Warning);
            _nameTextBox.Focus(); // 커서를 이름 칸으로 이동
            return;
        }

        // 선택된 과목 모으기
        string subjects = "";
        if (_chkMath.Checked) subjects += "수학 ";
        if (_chkScience.Checked) subjects += "과학 ";
        if (_chkEnglish.Checked) subjects += "영어 ";
        if (_chkArt.Checked) subjects += "미술 ";
        if (subjects == "") subjects = "없음";

        // 성별 확인
        string gender = _radioMale.Checked ? "남" : "여";

        // ListBox에 학생 정보 추가
        string entry = $"{_nameTextBox.Text} | {_ageTextBox.Text}세 | " +
                        $"{_gradeComboBox.SelectedItem} | {gender} | 과목: {subjects.Trim()}";
        _studentListBox.Items.Add(entry);

        // 상태 업데이트
        _statusLabel.Text = $"총 {_studentListBox.Items.Count}명 등록됨 - " +
                            $"마지막: {_nameTextBox.Text}";

        // 입력 필드 초기화
        _nameTextBox.Clear();
        _ageTextBox.Clear();
        _nameTextBox.Focus();
    }
}
