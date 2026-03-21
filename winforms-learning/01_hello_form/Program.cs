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
        Application.Run(new LessonForm());
    }
}

public sealed class LessonForm : Form
{
    public LessonForm()
    {
        lesson1BuildWindow();
        lesson2AddControls();
    }

    private void lesson1BuildWindow()
    {
        Text = "WinForms 첫 창";
        Size = new Size(420, 240);
        StartPosition = FormStartPosition.CenterScreen;
    }

    private void lesson2AddControls()
    {
        Controls.Add(new Label
        {
            Text = "폼(Form)은 눈에 보이는 창 전체입니다.",
            Location = new Point(20, 20),
            AutoSize = true
        });

        Controls.Add(new Button
        {
            Text = "버튼 예시",
            Location = new Point(20, 70),
            Size = new Size(120, 36)
        });
    }
}
