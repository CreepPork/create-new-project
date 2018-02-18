import os
import winreg
import subprocess
import datetime
import webbrowser

def main():
    # 1. Get the location of XAMPP (by registry first)
    try:
        xamppReg = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            'SOFTWARE\\WOW6432NODE\\xampp'
        )

        # Enum Value returns: value_name, value_data, value_data integer that identifies the data type
        xamppDirKey = winreg.EnumValue(xamppReg, 0)
        winreg.CloseKey(xamppReg)

        xamppDir = xamppDirKey[1]

        isValidKey = xamppDirKey[0] == 'Install_Dir'
        if (not isValidKey):
            raise ValueError('Got incorrect key name. Key name is: ' + xamppDirKey[0])

        if (not os.path.isdir(xamppDir)):
            raise ValueError('Registry path is not a directory!')

    except (WindowsError, ValueError):
        print ('Failed to find XAMPP installation directory.')
        xamppDir = input('XAMPP directory: ')

        if (xamppDir == ''):
            raise SyntaxError('Directory path can not be empty!')
        else:
            if (not os.path.isdir(xamppDir)):
                raise NotADirectoryError('Input is not a directory!')

    # 2. Ask the user for input
    YEAR = str(datetime.datetime.now().year)

    projectName = input('Project name: ')
    if (projectName == ''):
        raise SyntaxError('Project name can not be empty!')
    if (os.path.isdir(xamppDir + '\\htdocs\\' + YEAR + '\\' + projectName)):
        raise IsADirectoryError(projectName + ' directory already exists!')

    TRUE_TYPES = ['y', 'yes']
    FALSE_TYPES = ['n', 'no']

    isLaravel = input('Laravel project (y/n): ')
    if (isLaravel == ''):
        raise SyntaxError('Laravel check can not be empty!')
    if (not isLaravel in (TRUE_TYPES + FALSE_TYPES)):
        raise SyntaxError('Use only accepted entry types!')

    if (isLaravel in TRUE_TYPES): isLaravel = True
    if (isLaravel in FALSE_TYPES): isLaravel = False

    # 3. Create the directories
    try:
        # 3.1 Create the year directory if not present
        if (not os.path.isdir(xamppDir + '\\htdocs\\' + YEAR)):
            os.makedirs(xamppDir + '\\htdocs\\' + YEAR)

        # 3.2 Create the project directory
        os.makedirs(xamppDir + '\\htdocs\\' + YEAR + '\\' + projectName)

    except OSError:
        print ('Failed to create the required directories!')

    # 4. Stop the httpd (Apache) service
    subprocess.Popen(xamppDir + '\\apache_stop.bat', cwd=xamppDir)
    
    # 5. Add the config for vhosts
    apacheConfigVhosts = xamppDir + '\\apache\\conf\\extra\\httpd-vhosts.conf'

    if (isLaravel):
        public = '\\public'
    else:
        public = ''

    VHOSTSLINE1 = '\n\n<VirtualHost *:80>\n'
    VHOSTSLINE2 = '\tDocumentRoot "'+ xamppDir + '\\htdocs\\' + YEAR + '\\' + projectName + public +'"\n'
    VHOSTSLINE3 = '\tServerName '+ projectName +'.localhost\n'
    VHOSTSLINE4 = '\tErrorLog "logs/'+ projectName +'-error.log"\n'
    VHOSTSLINE5 = '\tCustomLog "logs/'+ projectName +'-access.log" common\n'
    VHOSTSLINE6 = '</VirtualHost>'

    open(apacheConfigVhosts, 'a').writelines([VHOSTSLINE1, VHOSTSLINE2, VHOSTSLINE3, VHOSTSLINE4, VHOSTSLINE5, VHOSTSLINE6])

    # 6. Start the httpd service
    subprocess.Popen(xamppDir + '\\apache_start.bat', cwd=xamppDir)

    # 7. Open the URL
    webbrowser.open('http://' + projectName + '.localhost')

    # 8. Cleanup
    print ('\nProject created!')
    print ('The ' + projectName + 'is available at: http://' + projectName + '.localhost!')

if __name__ == '__main__':
    main()