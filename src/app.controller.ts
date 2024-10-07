import {
  Controller,
  Get,
  Res,
  Post,
  UploadedFile,
  UseInterceptors,
  Query,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { exec, spawn } from 'child_process';
import { diskStorage } from 'multer';
import { extname, join } from 'path';
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
  uploadFile(
    @UploadedFile() file: any,
    @Res() res: Response,
    @Query() query: any,
  ) {
    let nomeDoArquivo: string;
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn('./enviroment/python.exe', [
        './python_backend/main.py',
        `../uploads/${file.filename}`,
        query.type,
      ]);

      // Obtendo o caminho atual
      const currentDirectory = __dirname; // Caminho atual do diretório
      console.log('Caminho atual:', currentDirectory);

      pythonProcess.stdout.on('data', (data) => {
        console.log(`Progress: ${data}`);
        if (data.toString().startsWith('ExcelFinal')) {
          const parts = data.toString().split(' ');
          if (parts.length > 1) {
            nomeDoArquivo = parts[1];
            nomeDoArquivo = parts[1].replace(/[\r\n]+$/, '');
          } else {
            console.log('Formato inesperado da string:', data);
          }
        }

        if (data.toString().startsWith('Fini')) {
          const filePath: string = join(
            currentDirectory,
            `../python_backend/${nomeDoArquivo}`,
          );

          res.setHeader('Access-Control-Allow-Origin', '*');

          if (true) {
            console.log('b');
            return res.download(filePath, (err) => {
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
      });

      pythonProcess.stderr.on('data', (data) => {
        // console.error(`Error: ${data}`);
        // reject(`Error: ${data}`);
      });
    });
  }
  @Get('download-excel')
  downloadExcel(@Res() res: Response) {}
}
