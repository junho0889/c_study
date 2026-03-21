// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WinForms 05 - 대화상자와 메시지박스                    ■
// ■  텍스트 편집기 + 다이얼로그 활용                        ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
//
// 이 파일에서 배우는 것:
//   1) MessageBox      - 알림창 (선생님이 "잘했어!" 또는 "틀렸어!" 하는 것)
//   2) OpenFileDialog  - 파일 열기 창 (서랍에서 공책 꺼내기)
//   3) SaveFileDialog  - 파일 저장 창 (공책을 서랍에 넣기)
//   4) ColorDialog     - 색상 선택 창 (물감 팔레트에서 색 고르기)
//   5) FontDialog      - 글꼴 선택 창 (글씨체 가게에서 글씨체 고르기)
//   6) 커스텀 다이얼로그 - 직접 만든 대화 창 (나만의 주문서)

using System;
using System.Drawing;
using System.IO;
using System.Windows.Forms;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new TextEditorForm());
    }
}

// ┌──────────────────────────────────────────────────┐
// │  텍스트 편집기 - 다이얼로그 활용 실습              │
// └──────────────────────────────────────────────────┘
public sealed class TextEditorForm : Form
{
    private readonly RichTextBox _editor;
    private readonly ToolStripStatusLabel _statusLabel;
    private string _currentFilePath = "";

    public TextEditorForm()
    {
        Text = "텍스트 편집기 - 다이얼로그 학습";
        Size = new Size(750, 550);
        StartPosition = FormStartPosition.CenterScreen;

        // ── 메뉴 구성 ──
        var menuStrip = new MenuStrip();

        var fileMenu = new ToolStripMenuItem("파일(&F)");
        fileMenu.DropDownItems.Add(new ToolStripMenuItem("열기(&O)...", null, OnOpen, Keys.Control | Keys.O));
        fileMenu.DropDownItems.Add(new ToolStripMenuItem("저장(&S)...", null, OnSave, Keys.Control | Keys.S));
        fileMenu.DropDownItems.Add(new ToolStripSeparator());
        fileMenu.DropDownItems.Add(new ToolStripMenuItem("종료(&X)", null, (s, e) => Close()));

        var formatMenu = new ToolStripMenuItem("서식(&O)");
        formatMenu.DropDownItems.Add(new ToolStripMenuItem("글꼴(&F)...", null, OnFontDialog));
        formatMenu.DropDownItems.Add(new ToolStripMenuItem("글자 색(&C)...", null, OnColorDialog));
        formatMenu.DropDownItems.Add(new ToolStripMenuItem("배경색(&B)...", null, OnBackColorDialog));

        var messageMenu = new ToolStripMenuItem("MessageBox 예제(&M)");
        messageMenu.DropDownItems.Add(new ToolStripMenuItem("정보 알림", null, OnInfoMessage));
        messageMenu.DropDownItems.Add(new ToolStripMenuItem("경고 알림", null, OnWarningMessage));
        messageMenu.DropDownItems.Add(new ToolStripMenuItem("오류 알림", null, OnErrorMessage));
        messageMenu.DropDownItems.Add(new ToolStripMenuItem("예/아니오 질문", null, OnYesNoMessage));
        messageMenu.DropDownItems.Add(new ToolStripMenuItem("예/아니오/취소", null, OnYesNoCancelMessage));
        messageMenu.DropDownItems.Add(new ToolStripMenuItem("다시 시도/취소", null, OnRetryCancelMessage));
        messageMenu.DropDownItems.Add(new ToolStripSeparator());
        messageMenu.DropDownItems.Add(new ToolStripMenuItem("커스텀 대화상자(&D)...", null, OnCustomDialog));

        menuStrip.Items.AddRange(new ToolStripItem[] { fileMenu, formatMenu, messageMenu });

        // ── 편집 영역 ──
        // RichTextBox는 일반 TextBox보다 더 많은 기능이 있습니다.
        // 글자마다 다른 색, 크기, 굵기를 적용할 수 있어요!
        // 일반 연필(TextBox) vs 색연필 세트(RichTextBox)
        _editor = new RichTextBox
        {
            Dock = DockStyle.Fill,
            Font = new Font("맑은 고딕", 12),
            AcceptsTab = true
        };

        // ── 상태 표시줄 ──
        var statusStrip = new StatusStrip();
        _statusLabel = new ToolStripStatusLabel("준비됨") { Spring = true };
        statusStrip.Items.Add(_statusLabel);

        Controls.Add(_editor);
        Controls.Add(menuStrip);
        Controls.Add(statusStrip);
        MainMenuStrip = menuStrip;
    }

    // ┌──────────────────────────────────────────┐
    // │  MessageBox - 모든 종류의 알림창           │
    // └──────────────────────────────────────────┘
    // MessageBox는 선생님이 학생에게 말하는 것과 같습니다.
    // "잘했어!" (Information), "조심해!" (Warning), "틀렸어!" (Error)
    // 그리고 "할래? 안 할래?" (YesNo) 같은 질문도 할 수 있어요.

    private void OnInfoMessage(object? sender, EventArgs e)
    {
        // ── 정보 알림 (파란 i 아이콘) ──
        // 선생님이 "오늘 숙제 없어요~" 하고 알려주는 것
        MessageBox.Show(
            "이것은 정보를 알려주는 메시지입니다.\n" +
            "사용자에게 참고할 내용을 전달할 때 씁니다.",
            "정보",                              // 제목
            MessageBoxButtons.OK,               // 확인 버튼만
            MessageBoxIcon.Information);        // i 아이콘
        _statusLabel.Text = "정보 메시지를 표시했습니다.";
    }

    private void OnWarningMessage(object? sender, EventArgs e)
    {
        // ── 경고 알림 (노란 ! 아이콘) ──
        // 선생님이 "복도에서 뛰지 마세요!" 하고 주의 주는 것
        MessageBox.Show(
            "이것은 경고 메시지입니다.\n" +
            "위험하거나 주의가 필요한 상황에서 씁니다.",
            "경고",
            MessageBoxButtons.OK,
            MessageBoxIcon.Warning);
        _statusLabel.Text = "경고 메시지를 표시했습니다.";
    }

    private void OnErrorMessage(object? sender, EventArgs e)
    {
        // ── 오류 알림 (빨간 X 아이콘) ──
        // 선생님이 "이건 틀렸어요!" 하고 알려주는 것
        MessageBox.Show(
            "이것은 오류 메시지입니다.\n" +
            "뭔가 잘못되었을 때 사용합니다.",
            "오류",
            MessageBoxButtons.OK,
            MessageBoxIcon.Error);
        _statusLabel.Text = "오류 메시지를 표시했습니다.";
    }

    private void OnYesNoMessage(object? sender, EventArgs e)
    {
        // ── 예/아니오 질문 ──
        // 선생님이 "이거 맞아? 틀려?" 하고 물어보는 것
        DialogResult result = MessageBox.Show(
            "정말로 내용을 지우시겠습니까?",
            "확인",
            MessageBoxButtons.YesNo,           // 예/아니오 두 버튼
            MessageBoxIcon.Question);          // ? 아이콘

        // 사용자가 누른 버튼에 따라 다르게 행동
        if (result == DialogResult.Yes)
            _statusLabel.Text = "'예'를 선택했습니다.";
        else
            _statusLabel.Text = "'아니오'를 선택했습니다.";
    }

    private void OnYesNoCancelMessage(object? sender, EventArgs e)
    {
        // ── 예/아니오/취소 ──
        // "저장할래? 안 할래? 아니면 취소할래?" 세 가지 선택
        DialogResult result = MessageBox.Show(
            "변경 사항을 저장하시겠습니까?",
            "저장 확인",
            MessageBoxButtons.YesNoCancel,
            MessageBoxIcon.Question);

        switch (result)
        {
            case DialogResult.Yes:
                _statusLabel.Text = "저장 후 계속합니다.";
                break;
            case DialogResult.No:
                _statusLabel.Text = "저장하지 않고 계속합니다.";
                break;
            case DialogResult.Cancel:
                _statusLabel.Text = "작업을 취소했습니다.";
                break;
        }
    }

    private void OnRetryCancelMessage(object? sender, EventArgs e)
    {
        // ── 다시 시도/취소 ──
        // "한 번 더 해볼래? 그만할래?"
        DialogResult result = MessageBox.Show(
            "파일을 찾을 수 없습니다. 다시 시도하시겠습니까?",
            "파일 오류",
            MessageBoxButtons.RetryCancel,
            MessageBoxIcon.Error);

        _statusLabel.Text = result == DialogResult.Retry
            ? "다시 시도합니다." : "취소했습니다.";
    }

    // ┌──────────────────────────────────────────┐
    // │  OpenFileDialog - 파일 열기 대화상자       │
    // └──────────────────────────────────────────┘
    // 서랍에서 공책을 꺼내는 것과 같습니다.
    // Filter: 어떤 종류의 파일만 보여줄지 정합니다 (국어 공책만? 수학 공책만?)
    private void OnOpen(object? sender, EventArgs e)
    {
        using var dialog = new OpenFileDialog
        {
            Title = "파일 열기",
            Filter = "텍스트 파일 (*.txt)|*.txt|모든 파일 (*.*)|*.*",
            // Filter 설명:
            // "보여줄 이름|확장자패턴" 형식
            // | 로 여러 필터를 구분
            FilterIndex = 1,          // 기본으로 첫 번째 필터 사용
            InitialDirectory = Environment.GetFolderPath(Environment.SpecialFolder.Desktop)
        };

        // ShowDialog()는 창을 열고 사용자가 선택할 때까지 기다립니다.
        // DialogResult.OK = 사용자가 "열기" 버튼을 눌렀다는 뜻
        if (dialog.ShowDialog() == DialogResult.OK)
        {
            try
            {
                _editor.Text = File.ReadAllText(dialog.FileName);
                _currentFilePath = dialog.FileName;
                Text = $"텍스트 편집기 - {Path.GetFileName(dialog.FileName)}";
                _statusLabel.Text = $"파일을 열었습니다: {dialog.FileName}";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"파일을 열 수 없습니다:\n{ex.Message}",
                    "오류", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }

    // ┌──────────────────────────────────────────┐
    // │  SaveFileDialog - 파일 저장 대화상자       │
    // └──────────────────────────────────────────┘
    // 공책을 서랍에 넣는 것과 같습니다.
    // 어느 서랍(폴더)에 넣을지, 이름을 뭐라고 쓸지 정합니다.
    private void OnSave(object? sender, EventArgs e)
    {
        using var dialog = new SaveFileDialog
        {
            Title = "파일 저장",
            Filter = "텍스트 파일 (*.txt)|*.txt|모든 파일 (*.*)|*.*",
            DefaultExt = "txt",           // 확장자를 안 쓰면 자동으로 .txt 추가
            FileName = _currentFilePath != "" ? Path.GetFileName(_currentFilePath) : "새 문서.txt"
        };

        if (dialog.ShowDialog() == DialogResult.OK)
        {
            try
            {
                File.WriteAllText(dialog.FileName, _editor.Text);
                _currentFilePath = dialog.FileName;
                Text = $"텍스트 편집기 - {Path.GetFileName(dialog.FileName)}";
                _statusLabel.Text = $"저장 완료: {dialog.FileName}";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"저장할 수 없습니다:\n{ex.Message}",
                    "오류", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }

    // ┌──────────────────────────────────────────┐
    // │  FontDialog - 글꼴 선택 대화상자           │
    // └──────────────────────────────────────────┘
    // 글씨체 가게에서 원하는 글씨체를 고르는 것과 같습니다.
    // 굵기, 크기, 이탤릭(기울임)도 한꺼번에 선택할 수 있어요.
    private void OnFontDialog(object? sender, EventArgs e)
    {
        using var dialog = new FontDialog
        {
            Font = _editor.Font,          // 현재 글꼴을 기본값으로
            ShowColor = true,             // 색상 선택도 포함
            ShowEffects = true            // 취소선, 밑줄 효과도 선택 가능
        };

        if (dialog.ShowDialog() == DialogResult.OK)
        {
            _editor.Font = dialog.Font;
            _statusLabel.Text = $"글꼴 변경: {dialog.Font.Name}, {dialog.Font.Size}pt";
        }
    }

    // ┌──────────────────────────────────────────┐
    // │  ColorDialog - 색상 선택 대화상자          │
    // └──────────────────────────────────────────┘
    // 물감 팔레트에서 원하는 색을 고르는 것과 같습니다.
    private void OnColorDialog(object? sender, EventArgs e)
    {
        using var dialog = new ColorDialog
        {
            Color = _editor.ForeColor,    // 현재 글자 색을 기본값으로
            FullOpen = true               // 커스텀 색상 패널도 바로 보여줌
        };

        if (dialog.ShowDialog() == DialogResult.OK)
        {
            _editor.ForeColor = dialog.Color;
            _statusLabel.Text = $"글자 색 변경: {dialog.Color.Name}";
        }
    }

    private void OnBackColorDialog(object? sender, EventArgs e)
    {
        using var dialog = new ColorDialog
        {
            Color = _editor.BackColor,
            FullOpen = true
        };

        if (dialog.ShowDialog() == DialogResult.OK)
        {
            _editor.BackColor = dialog.Color;
            _statusLabel.Text = $"배경색 변경: {dialog.Color.Name}";
        }
    }

    // ┌──────────────────────────────────────────┐
    // │  커스텀 대화상자 - 직접 만든 입력 창        │
    // └──────────────────────────────────────────┘
    // 기본 제공 대화상자로 부족할 때, 나만의 주문서를 만들 수 있습니다!
    private void OnCustomDialog(object? sender, EventArgs e)
    {
        using var dialog = new FindReplaceDialog();
        if (dialog.ShowDialog() == DialogResult.OK)
        {
            string findText = dialog.FindText;
            string replaceText = dialog.ReplaceText;

            if (!string.IsNullOrEmpty(findText))
            {
                _editor.Text = _editor.Text.Replace(findText, replaceText);
                _statusLabel.Text = $"'{findText}'를 '{replaceText}'로 바꿨습니다.";
            }
        }
    }
}

// ┌──────────────────────────────────────────────────┐
// │  커스텀 다이얼로그 폼 - 찾기/바꾸기 창             │
// └──────────────────────────────────────────────────┘
// Form을 상속받아서 나만의 대화상자를 만듭니다.
// 미리 만들어진 MessageBox로는 할 수 없는 복잡한 입력을
// 받을 때 사용합니다. 나만의 주문서를 만드는 것과 같아요!
public sealed class FindReplaceDialog : Form
{
    private readonly TextBox _findTextBox;
    private readonly TextBox _replaceTextBox;

    public string FindText => _findTextBox.Text;
    public string ReplaceText => _replaceTextBox.Text;

    public FindReplaceDialog()
    {
        Text = "찾기 및 바꾸기";
        Size = new Size(400, 200);
        FormBorderStyle = FormBorderStyle.FixedDialog; // 크기 조절 불가
        MaximizeBox = false;          // 최대화 버튼 숨김
        MinimizeBox = false;          // 최소화 버튼 숨김
        StartPosition = FormStartPosition.CenterParent; // 부모 폼 중앙에 표시

        // 찾을 문자열
        Controls.Add(new Label
        {
            Text = "찾을 내용:",
            Location = new Point(15, 20),
            AutoSize = true
        });
        _findTextBox = new TextBox
        {
            Location = new Point(100, 17),
            Size = new Size(250, 25)
        };
        Controls.Add(_findTextBox);

        // 바꿀 문자열
        Controls.Add(new Label
        {
            Text = "바꿀 내용:",
            Location = new Point(15, 55),
            AutoSize = true
        });
        _replaceTextBox = new TextBox
        {
            Location = new Point(100, 52),
            Size = new Size(250, 25)
        };
        Controls.Add(_replaceTextBox);

        // 확인/취소 버튼
        // DialogResult를 설정하면 버튼 클릭 시 자동으로 폼이 닫힙니다.
        var okButton = new Button
        {
            Text = "바꾸기",
            Location = new Point(180, 100),
            Size = new Size(80, 35),
            DialogResult = DialogResult.OK // 이 버튼을 누르면 OK 결과 반환
        };
        var cancelButton = new Button
        {
            Text = "취소",
            Location = new Point(270, 100),
            Size = new Size(80, 35),
            DialogResult = DialogResult.Cancel
        };

        Controls.Add(okButton);
        Controls.Add(cancelButton);

        AcceptButton = okButton;   // Enter키 = 확인
        CancelButton = cancelButton; // Esc키 = 취소
    }
}
