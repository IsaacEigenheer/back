import {
  Controller,
  Get,
  Res,
  Post,
  UploadedFile,
  UseInterceptors,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { exec, spawn } from 'child_process';
import { diskStorage } from 'multer';
import { extname } from 'path';
import { Response } from 'express';
import * as fs from 'fs';


@Controller('upload')
export class AppController {
  @Post()
  @UseInterceptors(
    FileInterceptor('file', {
      storage: diskStorage({
        destination: './uploads', // Pasta onde os arquivos serão salvos
        filename: (req, file, callback) => {
          // Define o nome do arquivo
          const uniqueSuffix = Math.round(Math.random() * 1e9);
          const ext = extname(file.originalname);
          const filename = `output${uniqueSuffix}${ext}`;
          callback(null, filename);
        },
      }),
    }),
  )
  uploadFile(@UploadedFile() file: any) {
    console.log(file); // Informações do arquivo (nome, path, etc.)
    return { message: 'File uploaded successfully', file };
  }

  @Get('start-python')
  startPythonScript() {
    console.log('iniciou');
    return new Promise((resolve, reject) => {
      console.log('1');
      const pythonProcess = spawn('./Project_20240710/python.exe', [
        './python_backend/main.py',
        '../uploads/output61714129322.pdf',
        'HPE',
      ]);
      console.log('2');
      pythonProcess.stdout.on('data', (data) => {
        console.log(`Progress: ${data}`);
      });
      console.log('3');
      pythonProcess.stderr.on('data', (data) => {
        console.error(`Error: ${data}`);
        reject(`Error: ${data}`);
      });
      console.log('4');
      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          reject(`Python script exited with code ${code}`);
        } else {
          resolve({
            message: 'Python script finished successfully',
          });
        }
      });
      console.log('5');

    });
  }

  @Get('download-excel')
  downloadExcel(@Res() res: Response) {
    const filePath: string = './python_backend/Excel/planilha_finaloutput6174129322.xlsx';

    res.setHeader('Access-Control-Allow-Origin', '*'); // Permite CORS

    if (fs.existsSync(filePath)) {
      res.download(filePath, (err) => {
        if (err) {
          console.error('Error downloading file:', err);
          res.status(500).send('Error downloading file');
        } else {
          fs.unlink(filePath, (err) => {
            if (err) {
              console.error('Error deleting file:', err);
            } else {
              console.log('File deleted successfully');
            }
          });
        }
      });
    } else {
      res.status(404).send('File not found');
    }
  }
  

}


