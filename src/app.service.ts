import { Injectable } from '@nestjs/common';
import { promises as fs } from 'fs';
import * as path from 'path'; // ou import path from 'path';

@Injectable()
export class AppService {
  getHello(): string {
    return 'Hello World!';
  }

  async generateExcel(): Promise<Buffer> {
    console.log(__dirname, '..');

    const filePath = path.join(
      __dirname,
      '..',
      'python_backend',
      'Excel',
      'planilha_finaloutput61714129322.xlsx',
    );

    console.log(filePath);

    // Leia o arquivo e retorne como um buffer
    return await fs.readFile(filePath);
  }
}
