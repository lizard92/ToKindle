# -*- coding: utf-8 -*-

import smtplib
import os
import sys

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import MAIL_HOST, MAIL_USER, MAIL_PWD, KINDLE_MAIL

class EmailSender(object):

    def __init__(self, mailHost, mailUser, mailPwd):
        self.mailHost = mailHost
        self.mailUser = mailUser
        self.mailPwd = mailPwd

    # send email with multi attachments
    def emailFile(self, sender, receiver, filePaths):
        if len(filePaths) == 0:
            print "附件名不能为空"
            return False

        msg = MIMEMultipart()

        first = filePaths[0]
        i = first.rfind(os.sep)
        if i != -1:
            subject = first[i+1:]
        else:
            subject = first
        if len(filePaths) > 1:
            subject = subject + "等" + str(len(filePaths)) + "个附件"

        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver

        # 按序构造附件列表
        map(msg.attach, [self.attachFile(filePath) for filePath in filePaths])

        try:
            s = smtplib.SMTP()
            s.connect(self.mailHost)
            s.starttls()
            s.login(self.mailUser, self.mailPwd)
            s.sendmail(sender, receiver, msg.as_string())
            s.quit()
        except smtplib.SMTPException, e:
            print "error:", e
            return False

        return True

    # return an attachment object with specific type
    def attachFile(self, filePath):
        i = filePath.rfind(os.sep)
        # 文件名
        if i != -1:
            fileName = filePath[i + 1 : ]
        else:
            fileName = filePath

        # 文件格式,以后缀区分
        i = fileName.rfind(".")
        if i != -1:
            suffix = fileName[i + 1 : ]
        else:
            suffix = "txt"

        # 根据附件的格式选择不同的读取方式:按字符还是按二进制字节
        try:
            if suffix in ["jpeg", "jpg", "png"]:
                att = MIMEText(open(filePath, "rb").read(), "base64", "utf-8")
            else:
                att = MIMEText(open(filePath, "r").read(), _charset = "utf-8")
        except IOError, e:
            print "error:", e
            print fileName + "读取失败,请检查文件是否存在"

        att["Content-Type"] = 'application/octet-stream'
        # filename will be displayed as attachment's name,should be extracted from filePath
        # 邮件中附件的名字即为该附件文件的名字
        att["Content-Disposition"] = "attachment; filename={fileName}".format(fileName = fileName)
        return att


if __name__ == "__main__":

    fileList = []
    for i in range(len(sys.argv)):
        if i > 0:
            fileList.append(sys.argv[i])

    e = EmailSender(MAIL_HOST, MAIL_USER, MAIL_PWD)
    print "邮件发送中……"
    if e.emailFile(MAIL_USER, KINDLE_MAIL, fileList):
        print "邮件已成功发送"
    else:
        print "邮件发送失败,请检查网络和参数重试"
