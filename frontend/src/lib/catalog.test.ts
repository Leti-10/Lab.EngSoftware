import { uniqueAuthors } from './catalog'

describe('uniqueAuthors', () => {
  it('remove autores repetidos com ou sem acento', () => {
    expect(uniqueAuthors(['Itamar Vieira Junior', 'Itamar Vieira Júnior', 'Outra Pessoa'])).toEqual(
      ['Itamar Vieira Junior', 'Outra Pessoa'],
    )
  })
})
