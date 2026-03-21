// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WinForms 04 - 메뉴와 도구 모음 (Menu & Toolbar)       ■
// ■  간단한 메모장 레이아웃 만들기                           ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
//
// 이 파일에서 배우는 것:
//   1) MenuStrip       - 화면 위쪽의 메뉴 바 (식당의 메뉴판)
//   2) ToolStrip       - 자주 쓰는 버튼 모음 (연필꽂이)
//   3) StatusStrip     - 화면 아래쪽 상태 표시줄 (자동차 계기판)
//   4) ContextMenuStrip - 마우스 오른쪽 클릭 메뉴 (숨겨진 비밀 서랍)
//   5) 키보드 단축키    - Ctrl+S 같은 빠른 명령 (지름길)

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
        Application.Run(new NotepadForm());
    }
}

// ┌──────────────────────────────────────────────────┐
// │  간단한 메모장 - 메뉴, 도구 모음, 상태 표시줄     │
// └──────────────────────────────────────────────────┘
public sealed class NotepadForm : Form
{
    private readonly TextBox _editor;
    private readonly StatusStrip _statusStrip;
    private readonly ToolStripStatusLabel _statusLabel;
    private readonly ToolStripStatusLabel _charCountLabel;
    private string _currentFileName = "새 문서";

    public NotepadForm()
    {
        Text = "미니 메모장 - 메뉴/도구 모음 학습";
        Size = new Size(700, 500);
        StartPosition = FormStartPosition.CenterScreen;

        // ┌──────────────────────────────────────────┐
        // │  1단계: MenuStrip - 메뉴판 만들기          │
        // └──────────────────────────────────────────┘
        // MenuStrip은 식당의 메뉴판과 같습니다.
        // "파일", "편집", "서식" 같은 큰 분류가 있고,
        // 각 분류 아래에 세부 메뉴가 있습니다.
        var menuStrip = new MenuStrip();

        // ── 파일 메뉴 ──
        var fileMenu = new ToolStripMenuItem("파일(&F)");
        // (&F)는 Alt+F 단축키를 만듭니다. 메뉴에서 F에 밑줄이 그어져요.

        // 새 문서: Ctrl+N 단축키
        var newItem = new ToolStripMenuItem("새 문서(&N)", null, OnNew, Keys.Control | Keys.N);
        // ShortcutKeys = Keys.Control | Keys.N 은 "Ctrl키와 N키를 동시에 누르면 실행"
        // 학교에서 "줄 맞춰!"라고 외치면 바로 줄을 서는 것처럼,
        // Ctrl+N을 누르면 바로 새 문서가 열립니다.

        var openItem = new ToolStripMenuItem("열기(&O)...", null, OnOpen, Keys.Control | Keys.O);
        var saveItem = new ToolStripMenuItem("저장(&S)", null, OnSave, Keys.Control | Keys.S);
        var exitItem = new ToolStripMenuItem("종료(&X)", null, OnExit, Keys.Alt | Keys.F4);

        // ToolStripSeparator는 메뉴 사이의 구분선입니다.
        // 식당 메뉴판에서 "---음료---" 줄로 구분하는 것처럼!
        fileMenu.DropDownItems.AddRange(new ToolStripItem[]
        {
            newItem, openItem, saveItem,
            new ToolStripSeparator(),
            exitItem
        });

        // ── 편집 메뉴 ──
        var editMenu = new ToolStripMenuItem("편집(&E)");
        var cutItem = new ToolStripMenuItem("잘라내기(&T)", null, OnCut, Keys.Control | Keys.X);
        var copyItem = new ToolStripMenuItem("복사(&C)", null, OnCopy, Keys.Control | Keys.C);
        var pasteItem = new ToolStripMenuItem("붙여넣기(&P)", null, OnPaste, Keys.Control | Keys.V);
        var selectAllItem = new ToolStripMenuItem("모두 선택(&A)", null, OnSelectAll, Keys.Control | Keys.A);

        editMenu.DropDownItems.AddRange(new ToolStripItem[]
        {
            cutItem, copyItem, pasteItem,
            new ToolStripSeparator(),
            selectAllItem
        });

        // ── 서식 메뉴 ──
        var formatMenu = new ToolStripMenuItem("서식(&O)");
        var wordWrapItem = new ToolStripMenuItem("자동 줄 바꿈(&W)");
        wordWrapItem.CheckOnClick = true; // 클릭하면 체크 표시가 토글됨
        wordWrapItem.Checked = true;
        wordWrapItem.Click += (s, e) =>
        {
            _editor.WordWrap = wordWrapItem.Checked;
        };

        var fontItem = new ToolStripMenuItem("글꼴(&F)...", null, OnFont);
        formatMenu.DropDownItems.AddRange(new ToolStripItem[] { wordWrapItem, fontItem });

        // ── 도움말 메뉴 ──
        var helpMenu = new ToolStripMenuItem("도움말(&H)");
        var aboutItem = new ToolStripMenuItem("정보(&A)", null, (s, e) =>
        {
            MessageBox.Show("미니 메모장 v1.0\nWinForms 메뉴/도구 모음 학습용",
                "정보", MessageBoxButtons.OK, MessageBoxIcon.Information);
        });
        helpMenu.DropDownItems.Add(aboutItem);

        menuStrip.Items.AddRange(new ToolStripItem[]
        {
            fileMenu, editMenu, formatMenu, helpMenu
        });

        // ┌──────────────────────────────────────────┐
        // │  2단계: ToolStrip - 도구 모음 만들기        │
        // └──────────────────────────────────────────┘
        // ToolStrip은 자주 쓰는 도구를 버튼으로 모아놓은 것입니다.
        // 책상 위 연필꽂이에 자주 쓰는 펜만 꽂아두는 것과 같아요!
        var toolStrip = new ToolStrip();

        var newButton = new ToolStripButton("새 문서") { ToolTipText = "새 문서 (Ctrl+N)" };
        newButton.Click += OnNew;

        var openButton = new ToolStripButton("열기") { ToolTipText = "열기 (Ctrl+O)" };
        openButton.Click += OnOpen;

        var saveButton = new ToolStripButton("저장") { ToolTipText = "저장 (Ctrl+S)" };
        saveButton.Click += OnSave;

        var cutButton = new ToolStripButton("잘라내기") { ToolTipText = "잘라내기 (Ctrl+X)" };
        cutButton.Click += OnCut;

        var copyButton = new ToolStripButton("복사") { ToolTipText = "복사 (Ctrl+C)" };
        copyButton.Click += OnCopy;

        var pasteButton = new ToolStripButton("붙여넣기") { ToolTipText = "붙여넣기 (Ctrl+V)" };
        pasteButton.Click += OnPaste;

        // ToolStripLabel: 도구 모음 안에 글자를 넣습니다 (이름표).
        var fontSizeLabel = new ToolStripLabel("글자 크기:");

        // ToolStripComboBox: 도구 모음 안에 드롭다운을 넣습니다.
        var fontSizeCombo = new ToolStripComboBox();
        fontSizeCombo.Items.AddRange(new object[] { "9", "10", "11", "12", "14", "16", "20", "24" });
        fontSizeCombo.SelectedIndex = 3; // 기본 12pt
        fontSizeCombo.SelectedIndexChanged += (s, e) =>
        {
            if (float.TryParse(fontSizeCombo.Text, out float size))
                _editor.Font = new Font(_editor.Font.FontFamily, size);
        };

        toolStrip.Items.AddRange(new ToolStripItem[]
        {
            newButton, openButton, saveButton,
            new ToolStripSeparator(),
            cutButton, copyButton, pasteButton,
            new ToolStripSeparator(),
            fontSizeLabel, fontSizeCombo
        });

        // ┌──────────────────────────────────────────┐
        // │  3단계: TextBox - 메모장 편집 영역          │
        // └──────────────────────────────────────────┘
        _editor = new TextBox
        {
            Multiline = true,           // 여러 줄 입력 가능
            Dock = DockStyle.Fill,      // 남은 공간을 모두 차지
            ScrollBars = ScrollBars.Both,// 가로/세로 스크롤바
            WordWrap = true,            // 자동 줄 바꿈
            AcceptsTab = true,          // Tab키로 들여쓰기 가능
            Font = new Font("맑은 고딕", 12)
        };
        // 텍스트가 바뀔 때마다 글자 수를 업데이트
        _editor.TextChanged += (s, e) =>
        {
            _charCountLabel.Text = $"글자 수: {_editor.TextLength}";
        };

        // ┌──────────────────────────────────────────┐
        // │  4단계: ContextMenuStrip - 우클릭 메뉴     │
        // └──────────────────────────────────────────┘
        // ContextMenuStrip은 마우스 오른쪽 버튼을 누르면 나타나는 메뉴입니다.
        // 숨겨진 비밀 서랍처럼, 필요할 때만 열어볼 수 있어요!
        var contextMenu = new ContextMenuStrip();
        contextMenu.Items.Add(new ToolStripMenuItem("잘라내기", null, OnCut));
        contextMenu.Items.Add(new ToolStripMenuItem("복사", null, OnCopy));
        contextMenu.Items.Add(new ToolStripMenuItem("붙여넣기", null, OnPaste));
        contextMenu.Items.Add(new ToolStripSeparator());
        contextMenu.Items.Add(new ToolStripMenuItem("모두 선택", null, OnSelectAll));

        _editor.ContextMenuStrip = contextMenu; // TextBox에 우클릭 메뉴 연결

        // ┌──────────────────────────────────────────┐
        // │  5단계: StatusStrip - 상태 표시줄           │
        // └──────────────────────────────────────────┘
        // StatusStrip은 자동차 계기판처럼 현재 상태를 보여줍니다.
        // 화면 맨 아래에 위치하여 파일 이름, 글자 수 등을 표시합니다.
        _statusStrip = new StatusStrip();

        _statusLabel = new ToolStripStatusLabel
        {
            Text = "준비됨",
            Spring = true, // 남은 공간을 차지 (스프링처럼 늘어남)
            TextAlign = ContentAlignment.MiddleLeft
        };

        _charCountLabel = new ToolStripStatusLabel
        {
            Text = "글자 수: 0",
            BorderSides = ToolStripStatusLabelBorderSides.Left,
            BorderStyle = Border3DStyle.Etched
        };

        _statusStrip.Items.AddRange(new ToolStripItem[]
        {
            _statusLabel, _charCountLabel
        });

        // ┌──────────────────────────────────────────┐
        // │  6단계: 컨트롤 추가 순서 (중요!)           │
        // └──────────────────────────────────────────┘
        // Dock을 사용할 때 추가 순서가 중요합니다!
        // 먼저 추가한 것이 먼저 자리를 잡습니다.
        // 도시락 싸기: 밥을 먼저 넣고 반찬을 넣는 것처럼,
        // 가장자리(Top, Bottom)를 먼저 채우고 Fill을 마지막에!
        Controls.Add(_editor);         // Fill - 남은 공간 전부
        Controls.Add(toolStrip);       // Top - 위쪽에 붙음
        Controls.Add(menuStrip);       // Top - 가장 위쪽
        Controls.Add(_statusStrip);    // Bottom - 아래쪽
        MainMenuStrip = menuStrip;
    }

    // ┌──────────────────────────────────────────┐
    // │  이벤트 핸들러 - 각 메뉴 기능 구현         │
    // └──────────────────────────────────────────┘
    private void OnNew(object? sender, EventArgs e)
    {
        if (_editor.TextLength > 0)
        {
            var result = MessageBox.Show("현재 문서를 저장하시겠습니까?",
                "새 문서", MessageBoxButtons.YesNoCancel, MessageBoxIcon.Question);
            if (result == DialogResult.Cancel) return;
        }
        _editor.Clear();
        _currentFileName = "새 문서";
        _statusLabel.Text = "새 문서가 만들어졌습니다.";
    }

    private void OnOpen(object? sender, EventArgs e)
    {
        _statusLabel.Text = "열기 기능 - 05_dialog에서 자세히 배웁니다!";
    }

    private void OnSave(object? sender, EventArgs e)
    {
        _statusLabel.Text = "저장 기능 - 05_dialog에서 자세히 배웁니다!";
    }

    private void OnCut(object? sender, EventArgs e)
    {
        if (_editor.SelectedText.Length > 0)
            _editor.Cut(); // 선택된 텍스트를 잘라내서 클립보드에 저장
        _statusLabel.Text = "잘라내기 완료";
    }

    private void OnCopy(object? sender, EventArgs e)
    {
        if (_editor.SelectedText.Length > 0)
            _editor.Copy(); // 선택된 텍스트를 클립보드에 복사
        _statusLabel.Text = "복사 완료";
    }

    private void OnPaste(object? sender, EventArgs e)
    {
        _editor.Paste(); // 클립보드에서 붙여넣기
        _statusLabel.Text = "붙여넣기 완료";
    }

    private void OnSelectAll(object? sender, EventArgs e)
    {
        _editor.SelectAll(); // 모든 텍스트 선택
        _statusLabel.Text = "모두 선택됨";
    }

    private void OnFont(object? sender, EventArgs e)
    {
        using var dialog = new FontDialog();
        dialog.Font = _editor.Font;
        if (dialog.ShowDialog() == DialogResult.OK)
        {
            _editor.Font = dialog.Font;
            _statusLabel.Text = $"글꼴: {dialog.Font.Name}, {dialog.Font.Size}pt";
        }
    }

    private void OnExit(object? sender, EventArgs e)
    {
        Close(); // 폼을 닫음 = 프로그램 종료
    }
}
